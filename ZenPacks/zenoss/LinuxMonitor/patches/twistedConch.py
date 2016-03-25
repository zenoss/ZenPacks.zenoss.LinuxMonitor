##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


# base library imports
import struct
from hashlib import md5, sha1, sha256

# external library imports
from Crypto import Util

# twisted imports
from twisted.internet import protocol
from twisted.python import log, randbytes

# sibling imports
from twisted.conch import error
from twisted.conch.ssh import keys
from twisted.conch.ssh.common import NS, getNS, MP, getMP, _MPpow, ffs
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.transport import (
    SSHTransportBase, SSHServerTransport, SSHClientTransport, SSHCiphers,
    _generateX,
    MSG_KEX_DH_GEX_REQUEST_OLD, MSG_KEX_DH_GEX_INIT, MSG_KEXDH_INIT,
    MSG_KEXDH_REPLY, MSG_KEX_DH_GEX_GROUP, MSG_KEX_DH_GEX_REPLY, MSG_KEXINIT,
    DISCONNECT_KEY_EXCHANGE_FAILED, DISCONNECT_HOST_KEY_NOT_VERIFIABLE,
)

# zope imports
from zope.interface import Attribute, implementer, Interface

# zenoss imports
from Products.ZenUtils.Utils import monkeypatch


"""
SSH key exchange handling.
"""


class _IKexAlgorithm(Interface):
    """
    An L{_IKexAlgorithm} describes a key exchange algorithm.
    """

    preference = Attribute(
        "An C{int} giving the preference of the algorithm when negotiating "
        "key exchange. Algorithms with lower precedence values are more "
        "preferred.")

    hashProcessor = Attribute(
        "A callable hash algorithm constructor (e.g. C{hashlib.sha256}) "
        "suitable for use with this key exchange algorithm.")


class _IFixedGroupKexAlgorithm(_IKexAlgorithm):
    """
    An L{_IFixedGroupKexAlgorithm} describes a key exchange algorithm with a
    fixed prime / generator group.
    """

    prime = Attribute(
        "A C{long} giving the prime number used in Diffie-Hellman key "
        "exchange, or C{None} if not applicable.")

    generator = Attribute(
        "A C{long} giving the generator number used in Diffie-Hellman key "
        "exchange, or C{None} if not applicable. (This is not related to "
        "Python generator functions.)")


class _IGroupExchangeKexAlgorithm(_IKexAlgorithm):
    """
    An L{_IGroupExchangeKexAlgorithm} describes a key exchange algorithm
    that uses group exchange between the client and server.

    A prime / generator group should be chosen at run time based on the
    requested size. See RFC 4419.
    """


@implementer(_IGroupExchangeKexAlgorithm)
class _DHGroupExchangeSHA256(object):
    """
    Diffie-Hellman Group and Key Exchange with SHA-256 as HASH. Defined in
    RFC 4419, 4.2.
    """

    preference = 1
    hashProcessor = sha256


@implementer(_IGroupExchangeKexAlgorithm)
class _DHGroupExchangeSHA1(object):
    """
    Diffie-Hellman Group and Key Exchange with SHA-1 as HASH. Defined in
    RFC 4419, 4.1.
    """

    preference = 2
    hashProcessor = sha1


@implementer(_IFixedGroupKexAlgorithm)
class _DHGroup1SHA1(object):
    """
    Diffie-Hellman key exchange with SHA-1 as HASH, and Oakley Group 2
    (1024-bit MODP Group). Defined in RFC 4253, 8.1.
    """

    preference = 3
    hashProcessor = sha1
    # Diffie-Hellman primes from Oakley Group 2 (RFC 2409, 6.2).
    prime = long('17976931348623159077083915679378745319786029604875601170644'
        '44236841971802161585193689478337958649255415021805654859805036464405'
        '48199239100050792877003355816639229553136239076508735759914822574862'
        '57500742530207744771258955095793777842444242661733472762929938766870'
        '9205606050270810842907692932019128194467627007L')
    generator = 2L


@implementer(_IFixedGroupKexAlgorithm)
class _DHGroup14SHA1(object):
    """
    Diffie-Hellman key exchange with SHA-1 as HASH and Oakley Group 14
    (2048-bit MODP Group). Defined in RFC 4253, 8.2.
    """

    preference = 4
    hashProcessor = sha1
    # Diffie-Hellman primes from Oakley Group 14 (RFC 3526, 3).
    prime = long('32317006071311007300338913926423828248817941241140239112842'
        '00975140074170663435422261968941736356934711790173790970419175460587'
        '32091950288537589861856221532121754125149017745202702357960782362488'
        '84246189477587641105928646099411723245426622522193230540919037680524'
        '23551912567971587011700105805587765103886184728025797605490356973256'
        '15261670813393617995413364765591603683178967290731783845896806396719'
        '00977202194168647225871031411336429319536193471636533209717077448227'
        '98858856536920864529663607725026895550592836275112117409697299806841'
        '05543595848665832916421362182310789909994486524682624169720359118525'
        '07045361090559L')
    generator = 2L


_kexAlgorithms = {
    "diffie-hellman-group-exchange-sha256": _DHGroupExchangeSHA256(),
    "diffie-hellman-group-exchange-sha1": _DHGroupExchangeSHA1(),
    "diffie-hellman-group1-sha1": _DHGroup1SHA1(),
    "diffie-hellman-group14-sha1": _DHGroup14SHA1(),
    }


def getKex(kexAlgorithm):
    """
    Get a description of a named key exchange algorithm.

    @param kexAlgorithm: The key exchange algorithm name.
    @type kexAlgorithm: C{str}

    @return: A description of the key exchange algorithm named by
        C{kexAlgorithm}.
    @rtype: L{_IKexAlgorithm}

    @raises ConchError: if the key exchange algorithm is not found.
    """
    if kexAlgorithm not in _kexAlgorithms:
        raise error.ConchError(
            "Unsupported key exchange algorithm: %s" % (kexAlgorithm,))
    return _kexAlgorithms[kexAlgorithm]


def isFixedGroup(kexAlgorithm):
    """
    Returns C{True} if C{kexAlgorithm} has a fixed prime / generator group.

    @param kexAlgorithm: The key exchange algorithm name.
    @type kexAlgorithm: C{str}

    @return: C{True} if C{kexAlgorithm} has a fixed prime / generator group,
        otherwise C{False}.
    @rtype: C{bool}
    """
    return _IFixedGroupKexAlgorithm.providedBy(getKex(kexAlgorithm))


def getHashProcessor(kexAlgorithm):
    """
    Get the hash algorithm callable to use in key exchange.

    @param kexAlgorithm: The key exchange algorithm name.
    @type kexAlgorithm: C{str}

    @return: A callable hash algorithm constructor (e.g. C{hashlib.sha256}).
    @rtype: C{callable}
    """
    kex = getKex(kexAlgorithm)
    return kex.hashProcessor


def getDHGeneratorAndPrime(kexAlgorithm):
    """
    Get the generator and the prime to use in key exchange.

    @param kexAlgorithm: The key exchange algorithm name.
    @type kexAlgorithm: C{str}

    @return: A C{tuple} containing C{long} generator and C{long} prime.
    @rtype: C{tuple}
    """
    kex = getKex(kexAlgorithm)
    return kex.generator, kex.prime


def getSupportedKeyExchanges():
    """
    Get a list of supported key exchange algorithm names in order of
    preference.

    @return: A C{list} of supported key exchange algorithm names.
    @rtype: C{list} of C{str}
    """
    return sorted(
        _kexAlgorithms,
        key = lambda kexAlgorithm: _kexAlgorithms[kexAlgorithm].preference)


"""
Patches.
"""


@monkeypatch(SSHTransportBase)
def __init__(self):
    self.supportedKeyExchanges = getSupportedKeyExchanges()
    self._kexAlg = None


@monkeypatch(SSHTransportBase)
def getKexAlg(self):
    """
    The key exchange algorithm name agreed between client and server.
    """
    return self._kexAlg


@monkeypatch(SSHTransportBase)
def setKexAlg(self, value):
    """
    Set the key exchange algorithm name.

    @raises ConchError: if the key exchange algorithm is not found.
    """
    # Check for supportedness.
    getKex(value)
    self._kexAlg = value


@monkeypatch(SSHTransportBase)
def _getKey(self, c, sharedSecret, exchangeHash):
    """
    Get one of the keys for authentication/encryption.

    @type c: C{str}
    @type sharedSecret: C{str}
    @type exchangeHash: C{str}
    """
    hashProcessor = getHashProcessor(self.getKexAlg())
    k1 = hashProcessor(sharedSecret + exchangeHash + c + self.sessionID)
    k1 = k1.digest()
    k2 = hashProcessor(sharedSecret + exchangeHash + k1).digest()
    return k1 + k2


@monkeypatch(SSHTransportBase)
def ssh_KEXINIT(self, packet):
    """
    Called when we receive a MSG_KEXINIT message.  Payload::
        bytes[16] cookie
        string keyExchangeAlgorithms
        string keyAlgorithms
        string incomingEncryptions
        string outgoingEncryptions
        string incomingAuthentications
        string outgoingAuthentications
        string incomingCompressions
        string outgoingCompressions
        string incomingLanguages
        string outgoingLanguages
        bool firstPacketFollows
        unit32 0 (reserved)

    Starts setting up the key exchange, keys, encryptions, and
    authentications.  Extended by ssh_KEXINIT in SSHServerTransport and
    SSHClientTransport.
    """
    self.otherKexInitPayload = chr(MSG_KEXINIT) + packet
    #cookie = packet[: 16] # taking this is useless
    k = getNS(packet[16:], 10)
    strings, rest = k[:-1], k[-1]
    (kexAlgs, keyAlgs, encCS, encSC, macCS, macSC, compCS, compSC, langCS,
     langSC) = [s.split(',') for s in strings]
    # these are the server directions
    outs = [encSC, macSC, compSC]
    ins = [encCS, macSC, compCS]
    if self.isClient:
        outs, ins = ins, outs # switch directions
    server = (self.supportedKeyExchanges, self.supportedPublicKeys,
            self.supportedCiphers, self.supportedCiphers,
            self.supportedMACs, self.supportedMACs,
            self.supportedCompressions, self.supportedCompressions)
    client = (kexAlgs, keyAlgs, outs[0], ins[0], outs[1], ins[1],
            outs[2], ins[2])
    if self.isClient:
        server, client = client, server
    self.setKexAlg(ffs(client[0], server[0]))
    self.keyAlg = ffs(client[1], server[1])
    self.nextEncryptions = SSHCiphers(
        ffs(client[2], server[2]),
        ffs(client[3], server[3]),
        ffs(client[4], server[4]),
        ffs(client[5], server[5]))
    self.outgoingCompressionType = ffs(client[6], server[6])
    self.incomingCompressionType = ffs(client[7], server[7])
    if None in (self.getKexAlg(), self.keyAlg, self.outgoingCompressionType,
                self.incomingCompressionType):
        self.sendDisconnect(DISCONNECT_KEY_EXCHANGE_FAILED,
                            "couldn't match all kex parts")
        return
    if None in self.nextEncryptions.__dict__.values():
        self.sendDisconnect(DISCONNECT_KEY_EXCHANGE_FAILED,
                            "couldn't match all kex parts")
        return
    log.msg('kex alg, key alg: %s %s' % (self.getKexAlg(), self.keyAlg))
    log.msg('outgoing: %s %s %s' % (self.nextEncryptions.outCipType,
                                    self.nextEncryptions.outMACType,
                                    self.outgoingCompressionType))
    log.msg('incoming: %s %s %s' % (self.nextEncryptions.inCipType,
                                    self.nextEncryptions.inMACType,
                                    self.incomingCompressionType))

    if self._keyExchangeState == self._KEY_EXCHANGE_REQUESTED:
        self._keyExchangeState = self._KEY_EXCHANGE_PROGRESSING
    else:
        self.sendKexInit()

    return kexAlgs, keyAlgs, rest # for SSHServerTransport to use


@monkeypatch(SSHServerTransport)
def _ssh_KEXDH_INIT(self, packet):
    """
    Called to handle the beginning of a non-group key exchange.

    Unlike other message types, this is not dispatched automatically.  It
    is called from C{ssh_KEX_DH_GEX_REQUEST_OLD} because an extra check is
    required to determine if this is really a KEXDH_INIT message or if it
    is a KEX_DH_GEX_REQUEST_OLD message.

    The KEXDH_INIT payload::

            integer e (the client's Diffie-Hellman public key)

    We send the KEXDH_REPLY with our host key and signature.
    """
    clientDHpublicKey, foo = getMP(packet)
    y = _getRandomNumber(randbytes.secureRandom, 512)
    self.g, self.p = getDHGeneratorAndPrime(self.getKexAlg())
    serverDHpublicKey = _MPpow(self.g, y, self.p)
    sharedSecret = _MPpow(clientDHpublicKey, y, self.p)
    h = sha1()
    h.update(NS(self.otherVersionString))
    h.update(NS(self.ourVersionString))
    h.update(NS(self.otherKexInitPayload))
    h.update(NS(self.ourKexInitPayload))
    h.update(NS(self.factory.publicKeys[self.keyAlg].blob()))
    h.update(MP(clientDHpublicKey))
    h.update(serverDHpublicKey)
    h.update(sharedSecret)
    exchangeHash = h.digest()
    self.sendPacket(
        MSG_KEXDH_REPLY,
        NS(self.factory.publicKeys[self.keyAlg].blob()) +
        serverDHpublicKey +
        NS(self.factory.privateKeys[self.keyAlg].sign(exchangeHash)))
    self._keySetup(sharedSecret, exchangeHash)


@monkeypatch(SSHServerTransport)
def ssh_KEX_DH_GEX_REQUEST_OLD(self, packet):
    """
    This represents different key exchange methods that share the same
    integer value.  If the message is determined to be a KEXDH_INIT,
    C{_ssh_KEXDH_INIT} is called to handle it.  Otherwise, for
    KEX_DH_GEX_REQUEST_OLD payload::

            integer ideal (ideal size for the Diffie-Hellman prime)

        We send the KEX_DH_GEX_GROUP message with the group that is
        closest in size to ideal.

    If we were told to ignore the next key exchange packet by ssh_KEXINIT,
    drop it on the floor and return.
    """
    if self.ignoreNextPacket:
        self.ignoreNextPacket = 0
        return

    # KEXDH_INIT and KEX_DH_GEX_REQUEST_OLD have the same value, so use
    # another cue to decide what kind of message the peer sent us.
    if isFixedGroup(self.getKexAlg()):
        return self._ssh_KEXDH_INIT(packet)
    else:
        self.dhGexRequest = packet
        ideal = struct.unpack('>L', packet)[0]
        self.g, self.p = self.factory.getDHPrime(ideal)
        self.sendPacket(MSG_KEX_DH_GEX_GROUP, MP(self.p) + MP(self.g))


@monkeypatch(SSHServerTransport)
def ssh_KEX_DH_GEX_REQUEST(self, packet):
    """
    Called when we receive a MSG_KEX_DH_GEX_REQUEST message.  Payload::
        integer minimum
        integer ideal
        integer maximum

    The client is asking for a Diffie-Hellman group between minimum and
    maximum size, and close to ideal if possible.  We reply with a
    MSG_KEX_DH_GEX_GROUP message.

    If we were told to ignore the next key exchange packet by ssh_KEXINIT,
    drop it on the floor and return.
    """
    if self.ignoreNextPacket:
        self.ignoreNextPacket = 0
        return
    self.dhGexRequest = packet
    min, ideal, max = struct.unpack('>3L', packet)
    self.g, self.p = self.factory.getDHPrime(ideal)
    self.sendPacket(MSG_KEX_DH_GEX_GROUP, MP(self.p) + MP(self.g))
    

@monkeypatch(SSHServerTransport)
def ssh_KEX_DH_GEX_INIT(self, packet):
    """
    Called when we get a MSG_KEX_DH_GEX_INIT message.  Payload::
        integer e (client DH public key)

    We send the MSG_KEX_DH_GEX_REPLY message with our host key and
    signature.
    """
    clientDHpublicKey, foo = getMP(packet)
    # TODO: we should also look at the value they send to us and reject
    # insecure values of f (if g==2 and f has a single '1' bit while the
    # rest are '0's, then they must have used a small y also).

    # TODO: This could be computed when self.p is set up
    #  or do as openssh does and scan f for a single '1' bit instead

    pSize = Util.number.size(self.p)
    y = _getRandomNumber(randbytes.secureRandom, pSize)

    serverDHpublicKey = _MPpow(self.g, y, self.p)
    sharedSecret = _MPpow(clientDHpublicKey, y, self.p)
    h = getHashProcessor(self.getKexAlg())()
    h.update(NS(self.otherVersionString))
    h.update(NS(self.ourVersionString))
    h.update(NS(self.otherKexInitPayload))
    h.update(NS(self.ourKexInitPayload))
    h.update(NS(self.factory.publicKeys[self.keyAlg].blob()))
    h.update(self.dhGexRequest)
    h.update(MP(self.p))
    h.update(MP(self.g))
    h.update(MP(clientDHpublicKey))
    h.update(serverDHpublicKey)
    h.update(sharedSecret)
    exchangeHash = h.digest()
    self.sendPacket(
        MSG_KEX_DH_GEX_REPLY,
        NS(self.factory.publicKeys[self.keyAlg].blob()) +
        serverDHpublicKey +
        NS(self.factory.privateKeys[self.keyAlg].sign(exchangeHash)))
    self._keySetup(sharedSecret, exchangeHash)


@monkeypatch(SSHClientTransport)
def ssh_KEXINIT(self, packet):
    """
    Called when we receive a MSG_KEXINIT message.  For a description
    of the packet, see SSHTransportBase.ssh_KEXINIT().  Additionally,
    this method sends the first key exchange packet.  If the agreed-upon
    exchange has a fixed prime/generator group, generate a public key
    and send it in a MSG_KEXDH_INIT message. Otherwise, ask for a 2048
    bit group with a MSG_KEX_DH_GEX_REQUEST_OLD message.
    """
    if SSHTransportBase.ssh_KEXINIT(self, packet) is None:
        return # we disconnected
    if isFixedGroup(self.getKexAlg()):
        self.x = _generateX(randbytes.secureRandom, 512)
        self.g, self.p = getDHGeneratorAndPrime(self.getKexAlg())
        self.e = _MPpow(self.g, self.x, self.p)
        self.sendPacket(MSG_KEXDH_INIT, self.e)
    else:
        self.sendPacket(MSG_KEX_DH_GEX_REQUEST_OLD, '\x00\x00\x08\x00')


@monkeypatch(SSHClientTransport)
def _ssh_KEXDH_REPLY(self, packet):
    """
    Called to handle a reply to a non-group key exchange message
    (KEXDH_INIT).

    Like the handler for I{KEXDH_INIT}, this message type has an
    overlapping value.  This method is called from C{ssh_KEX_DH_GEX_GROUP}
    if that method detects a non-group key exchange is in progress.

    Payload::

        string serverHostKey
        integer f (server Diffie-Hellman public key)
        string signature

    We verify the host key by calling verifyHostKey, then continue in
    _continueKEXDH_REPLY.
    """
    pubKey, packet = getNS(packet)
    f, packet = getMP(packet)
    signature, packet = getNS(packet)
    fingerprint = ':'.join([ch.encode('hex') for ch in
                            md5(pubKey).digest()])
    d = self.verifyHostKey(pubKey, fingerprint)
    d.addCallback(self._continueKEXDH_REPLY, pubKey, f, signature)
    d.addErrback(
        lambda unused: self.sendDisconnect(
            DISCONNECT_HOST_KEY_NOT_VERIFIABLE, 'bad host key'))
    return d


@monkeypatch(SSHClientTransport)
def ssh_KEX_DH_GEX_GROUP(self, packet):
    """
    This handles different messages which share an integer value.

    If the key exchange does not have a fixed prime/generator group,
    we generate a Diffie-Hellman public key and send it in a
    MSG_KEX_DH_GEX_INIT message.

    Payload::
        string g (group generator)
        string p (group prime)
    """
    if isFixedGroup(self.getKexAlg()):
        return self._ssh_KEXDH_REPLY(packet)
    else:
        self.p, rest = getMP(packet)
        self.g, rest = getMP(rest)
        self.x = _generateX(randbytes.secureRandom, 320)
        self.e = _MPpow(self.g, self.x, self.p)
        self.sendPacket(MSG_KEX_DH_GEX_INIT, self.e)
        

@monkeypatch(SSHClientTransport)
def _continueGEX_REPLY(self, ignored, pubKey, f, signature):
    """
    The host key has been verified, so we generate the keys.

    @param pubKey: the public key blob for the server's public key.
    @type pubKey: C{str}
    @param f: the server's Diffie-Hellman public key.
    @type f: C{long}
    @param signature: the server's signature, verifying that it has the
        correct private key.
    @type signature: C{str}
    """
    serverKey = keys.Key.fromString(pubKey)
    sharedSecret = _MPpow(f, self.x, self.p)
    h = getHashProcessor(self.getKexAlg())()
    h.update(NS(self.ourVersionString))
    h.update(NS(self.otherVersionString))
    h.update(NS(self.ourKexInitPayload))
    h.update(NS(self.otherKexInitPayload))
    h.update(NS(pubKey))
    h.update('\x00\x00\x08\x00')
    h.update(MP(self.p))
    h.update(MP(self.g))
    h.update(self.e)
    h.update(MP(f))
    h.update(sharedSecret)
    exchangeHash = h.digest()
    if not serverKey.verify(signature, exchangeHash):
        self.sendDisconnect(DISCONNECT_KEY_EXCHANGE_FAILED,
                            'bad signature')
        return
    self._keySetup(sharedSecret, exchangeHash)


@monkeypatch(SSHFactory)
def buildProtocol(self, addr):
    """
    Create an instance of the server side of the SSH protocol.

    @type addr: L{twisted.internet.interfaces.IAddress} provider
    @param addr: The address at which the server will listen.

    @rtype: L{twisted.conch.ssh.SSHServerTransport}
    @return: The built transport.
    """
    t = protocol.Factory.buildProtocol(self, addr)
    t.supportedPublicKeys = self.privateKeys.keys()
    if not self.primes:
        log.msg('disabling non-fixed-group key exchange algorithms '
                'because we cannot find moduli file')
        t.supportedKeyExchanges = [
            kexAlgorithm for kexAlgorithm in t.supportedKeyExchanges
            if isFixedGroup(kexAlgorithm)]
    return t
