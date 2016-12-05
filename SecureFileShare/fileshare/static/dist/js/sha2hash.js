function sha2sum(oFile, last) {
            //var oFile = document.getElementById('uploadFile').files[0];
	//var fHash = document.getElementById('fileHash')
	var filehash;
    var sha2 = CryptoJS.algo.SHA256.create();
    var read = 0;
    var unit = 1024 * 1024;
    var blob;
	var reader = new FileReader();
	reader.readAsArrayBuffer(oFile.slice(read, read + unit));
	reader.onload = function(e) {
		var bytes = CryptoJS.lib.WordArray.create(e.target.result);
		sha2.update(bytes);
		read += unit;
		if (read < oFile.size) {
			blob = oFile.slice(read, read + unit);
			reader.readAsArrayBuffer(blob);
		} else {
			var hash = sha2.finalize();
			var hash_value = hash.toString(CryptoJS.enc.Hex);
			//console.log(hash_value); // print the result
			filehash={"filename":oFile.name, "file_hash":hash_value};
			file_hash.push(filehash);
			if (last)
				saveHash(file_hash);
		}
	}
}

var file_hash = [];
function getFileHash(elementId) {
	var oFiles = document.getElementById(elementId).files;
	var last = false;
	for (var i=0; i<oFiles.length; i++) {
		if (i === oFiles.length-1) {
			last = true;
		}
		sha2sum(oFiles[i],last);
	}
}

var data = []
function saveHash(fileHashValue) {
	console.log("fileHashValue: " + JSON.stringify(fileHashValue));
	for (var i=0; i<fileHashValue.length; i++){
		data.push(fileHashValue[i]);
	}
	document.getElementById('fileHash').value=JSON.stringify(data);
}
