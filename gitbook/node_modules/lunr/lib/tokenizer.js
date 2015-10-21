/*!
 * lunr.tokenizer
 * Copyright (C) @YEAR Oliver Nightingale
 */

/**
 * A function for splitting a string into tokens ready to be inserted into
 * the search index.
 *
 * @module
 * @param {String} obj The string to convert into tokens
 * @returns {Array}
 */
if(typeof module !== 'undefined' && module.exports){
  nodejieba_segment = require("nodejieba")
  nodejieba_segment.queryLoadDict(__dirname + "/node_modules/nodejieba/dict/jieba.dict.utf8", __dirname + "/node_modules/nodejieba/dict/hmm_model.utf8")
}
lunr.tokenizer = function (obj) {
  if (!arguments.length || obj == null || obj == undefined) return []
  if (Array.isArray(obj)) return obj.map(function (t) { return t.toLowerCase() })

  var str = obj.toString().replace(/^\s+/, '')

  for (var i = str.length - 1; i >= 0; i--) {
    if (/\S/.test(str.charAt(i))) {
      str = str.substring(0, i + 1)
      break
    }
  }

  if(typeof nodejieba_segment !== "undefined"){
    var wordList = nodejieba_segment.queryCutSync(str);

    return wordList
      .map(function (token) {
        return token.toLowerCase()
      })
  }else{

    return str
      .split(/(?:\s+|\-)/)
      .filter(function (token) {
        return !!token
      })
      .map(function (token) {
        return token.toLowerCase()
      })
  }
}
