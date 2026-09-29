var Class = Java.type("java.lang.Class");
var result = "";
var classes = [
  "com.fr.plugin.bigScreen.v11.BigScreenProvider",
  "com.fr.plugin.operation.v11.OperationPlugin",
  "com.fr.plugin.data.portal.v11.DataPortalProvider",
  "com.fr.plugin.data.sentinel.v11.DataSentinelPlugin",
  "com.fr.plugin.mobile.web.v11.MobileWebPlugin"
];
for (var i = 0; i < classes.length; i++) {
  try {
    var c = Class.forName(classes[i]);
    result += c.getName() + " loaded from " + c.getProtectionDomain().getCodeSource().getLocation() + "\n";
  } catch(e) {
    result += classes[i] + ": " + e.getMessage() + "\n";
  }
}
result;
