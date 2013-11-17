	var textareas = document.getElementsByTagName('textarea'),
	    permalink = document.getElementById('permalink'),
	    regexBinaryGroup = /\s*[01]{8}\s*/g,
	    regexAnyCharacter = /[\s\S]/g,
	    regexBinary = /^(\s*[01]{8}\s*)*$/,
	    regexExtendedASCII = /^[\x00-\xff]*$/,
	    // http://mathiasbynens.be/notes/localstorage-pattern
	    storage = (function() {
	    	var uid = new Date,
	    	    storage,
	    	    result;
	    	try {
	    		(storage = window.localStorage).setItem(uid, uid);
	    		result = storage.getItem(uid) == uid;
	    		storage.removeItem(uid);
	    		return result && storage;
	    	} catch(e) {}
	    }()),
	    stringFromCharCode = String.fromCharCode;

	function encode(string) {
		// URL-encode some more characters to avoid issues when using permalink URLs in Markdown
		return encodeURIComponent(string).replace(/['()_*]/g, function(character) {
			return '%' + character.charCodeAt().toString(16);
		});
	}

	function zeroPad(number) {
		return '00000000'.slice(String(number).length) + number;
	}

	function toASCII(string) {
		return string.replace(regexBinaryGroup, function(group) {
			return stringFromCharCode(parseInt(group, 2));
		});
	}

	function toBinary(string) {
		return string.replace(regexAnyCharacter, function(character) {
			return zeroPad(character.charCodeAt().toString(2)) + ' ';
		});
	}
