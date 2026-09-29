var result = "";
try {
  var f = new java.io.File("D:/FineReport_10.0/webapps/webroot/WEB-INF/lib/fine-activator-10.0.jar");
  result += "activator exists: " + f.exists() + "\n";
  var zip = new java.util.zip.ZipFile(f);
  var entries = zip.entries();
  var count = 0;
  while (entries.hasMoreElements()) {
    var e = entries.nextElement();
    var name = e.getName();
    if (name.indexOf("key") >= 0 || name.indexOf("encrypt") >= 0 || name.indexOf("assist") >= 0 || name.indexOf("plugin") >= 0) {
      if (count < 30) {
        result += name + " (" + e.getSize() + ")\n";
      }
      count++;
    }
  }
  result += "Total matching entries: " + count + "\n";

  // try key.txt
  var entry = zip.getEntry("com/fr/stable/plugin/key.txt");
  if (entry != null) {
    var is = zip.getInputStream(entry);
    var bytes = java.lang.reflect.Array.newInstance(java.lang.Byte.TYPE, 100);
    var len = is.read(bytes);
    is.close();
    var sb = new java.lang.StringBuilder();
    for (var i = 0; i < len; i++) {
      sb.append(java.lang.Integer.toHexString(bytes[i] & 0xff));
      if (i < len-1) sb.append(" ");
    }
    result += "\nkey.txt (" + len + " bytes hex): " + sb.toString();
  } else {
    result += "\nkey.txt NOT FOUND in jar";
  }
  zip.close();
} catch(e) { result += "Error: " + e.toString(); }
result;
