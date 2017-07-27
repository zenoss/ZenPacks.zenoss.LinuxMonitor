Ext.apply(Zenoss.render, {
    zenpacklib_ZenPacks_zenoss_LinuxMonitor_fileSystemStorageDevice: function(obj, metaData, record, rowIndex, colIndex) {
        if (typeof(obj) == "object") {
            var sameDevice = new RegExp("^" + this.uid).test(obj.uid);
            if (sameDevice) {
                return Zenoss.render.zenpacklib_ZenPacks_zenoss_LinuxMonitor_entityLinkFromGrid(obj, metaData, record, rowIndex, colIndex);
            } else{
                return Zenoss.render.link(obj);
            }
        }

        return obj;
    },

    zenpacklib_ZenPacks_zenoss_LinuxMonitor_percentage: function(value) {
        if (value === "Unknown" || value < 0) {
            return _t("Unknown");
        } else {
            return value + "%";
        }
    }
});
