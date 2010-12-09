function(head, req) {
  var row;
  var first = 1;
  var keys = [];
  var replaceAll = function(text, strA, strB) 
  {
      /*http://www.muellerdesigns.net/dasblog/2005/12/06/JavaScriptReplaceAllFunctionality.aspx*/
      if (typeof text != "string")
        return text;
      while ( text.indexOf(strA) != -1)
      {
          text = text.replace(strA,strB);
      }
      return text;
  }
  var flatten = function(obj, keys, prefix){
    prefix = prefix || "";
    keys = keys || 0;
    out = [];
    if (typeof obj != "object"){
      if (keys)
        out.push(prefix);
      else
        out.push(replaceAll(obj, "\"", "\\\""));
    } else {
      for (i in obj){
        out = out.concat(flatten(obj[i], keys, (prefix != '' ? prefix + '__' : '') + i));
      }
    }
    return out;
  }
  start({
    "headers": {
      "Content-Type": "text/csv"
     }
  });
  while(row = getRow()) {
    if (first){
      keys = flatten(row.value, 1);
      send('"' + keys.join('","') + '"' + "\n");
      first = 0;
    }
    var outs = [];
    for (i in keys){
      var key = keys[i];
      var elem = row.value;
      while (key.indexOf('__') !== -1){
        if (!(key.substring(0, key.indexOf('__')) in elem) || (typeof elem != 'object')){
          elem = null;
          break;
        }
        elem = elem[key.substring(0, key.indexOf('__'))];
        key = key.substring(key.indexOf('__') + 2);
      }
      if (elem == null || !(key in elem))
        outs.push(null);
      else
        outs.push(replaceAll(elem[key], "\"", "\\\""));
    }
    send('"' + outs.join('","') + '"' + "\n");
  }
}
