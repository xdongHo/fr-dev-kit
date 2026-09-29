var Class = Java.type("java.lang.Class");
var result = "";
var plugins = [
  "com.fr.plugin.fvs.FvsPlugin",
  "com.fr.plugin.bigScreen.v11.BigScreenPlugin",
  "com.fr.plugin.data.portal.v11.DataPortalProvider",
  "com.fr.plugin.data.sentinel.v11.DataSentinelPlugin",
  "com.fr.plugin.operation.v11.OperationPlugin",
  "com.fr.plugin.cloud.analytics.v11.CloudAnalyticsPlugin",
  "com.fr.plugin.mobile.web.v11.MobileWebPlugin"
];
for (var i = 0; i < plugins.length; i++) {
  try {
    Class.forName(plugins[i]);
    result += "FOUND: " + plugins[i] + "\n";
  } catch(e) {
    result += "NOT FOUND: " + plugins[i] + "\n";
  }
}
result;
