function reverse_to_str() {
    document.getElementById('plaintext').value = reverse(document.getElementById('reverse').value);
}

function str_to_reverse() {
    document.getElementById('reverse').value = reverse(document.getElementById('plaintext').value);
}

function str_to_eb64() {
    document.getElementById('8x-base64').value = btoa(btoa(btoa(btoa(btoa(btoa(btoa(btoa(document.getElementById('plaintext').value))))))));
}

function eb64_to_str() {
    document.getElementById('plaintext').value = atob(atob(atob(atob(atob(atob(atob(atob(document.getElementById('8x-base64').value.replace(/ /g,'')))))))));
}

function str_to_qbf() {
    document.getElementById('qbf').value = Symbolfuck.encode(document.getElementById('plaintext').value);
}

function qbf_to_str() {
    document.getElementById('plaintext').value = Symbolfuck.decode(document.getElementById('qbf').value.replace(/ /g,''));
}

function str_to_fhspeak() {
    document.getElementById('fhspeak').value = fhspeak.encode(document.getElementById('plaintext').value);
}

function fhspeak_to_str() {
    document.getElementById('plaintext').value = fhspeak.decode(document.getElementById('fhspeak').value.replace(/ /g,''));
}

function str_to_binary() {
    document.getElementById('binary').value = toBinary(document.getElementById('plaintext').value);
}

function binary_to_str() {
    document.getElementById('plaintext').value = toASCII(document.getElementById('binary').value.replace(/[ea\.\\?nN=lx]/g, "0").replace(/[hE1O\\!o)-]/g, "1").replace(/ /g,''));
}

function str_to_goomy() {
    document.getElementById('goomy').value = sstr_to_b64(document.getElementById('plaintext').value);
}

function goomy_to_str() {
    document.getElementById('plaintext').value = b64_to_sstr(document.getElementById('goomy').value)
}

function str_to_b64() {
    document.getElementById('base64').value = Base64.encode(document.getElementById('plaintext').value);
}

function b64_to_str() {
    document.getElementById('plaintext').value = Base64.decode(document.getElementById('base64').value.replace(/ /g,''));
}

function binary_to_fmorse() {
    morse = document.getElementById('binary').value.replace(/ /g, "").replace(/[ea0\\?n=lx]/g, ".").replace(/[hE1O\\!o)]/g, "-");
    newmorse = "";
    counter = 0;
    for (var i = 0; i < morse.length; ++i) {
        counter += 1;
        newmorse += morse[i];
        if ((morse[i] == "." && counter >= 3) || (morse[i] == "-" && counter >= 4)) {
            newmorse += " ";
            counter = 0;
        }
    }
    document.getElementById('binary').value = newmorse;
}

function binary_to_rfmorse() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/0/g, "-").replace(/1/g, ".");
}

function binary_to_circlefuck() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/[ea\.\\?n=lx]/g, "0").replace(/[hE1\\!o)-]/g, "O").replace(/ /g, "");
}

function binary_to_wtf() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/[ea\.0n=lx]/g, "?").replace(/[hE1Oo)-]/g, "!").replace(/ /g, "");
}

function binary_to_mockery() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/[e0\.\\?n=lx]/g, "a").replace(/[O1E\\!o)-]/g, "h").replace(/ /g, "");
}

function binary_to_mockery2() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/[e0\.\\?n=ax]/g, "l").replace(/[O1E\\!o)h-]/g, "o").replace(/ /g, "");
}

function binary_to_e() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/[a0\.\\?n=xl]/g, "e").replace(/[h1O\\!o)-]/g, "E").replace(/ /g, "");
}

function binary_to_xoxo() {
    document.getElementById('binary').value = document.getElementById('binary').value.replace(/[a0\.\\?e=ln]/g, "x").replace(/[h1O\\!E)o-]/g, "o").replace(/ /g, "");
}

function binary_to_nono() {
    nono = document.getElementById('binary').value.replace(/[a0\.\\?e=xl]/g, "n").replace(/[h1O\\!E)-]/g, "o").replace(/ /g, "");
    newnono = ""
    var o = 0;
    for (var i = 0; i<nono.length; ++i) {
        if (nono[i].toLowerCase() == "n") {
            if (o !== 0) {
                newnono = newnono + " ";
                o = 0;
            }
            newnono = newnono + "n";
        }
        else {
            newnono = newnono + "o";
            ++o;
        }
    }
    document.getElementById('binary').value = newnono;
}

function binary_to_smilies() {
    nono = document.getElementById('binary').value.replace(/[a0\.\\?enl]/g, "=").replace(/[h1O\\!Eo-]/g, ")").replace(/ /g, "");
    newnono = "";
    var o = 0;
    for (var i = 0; i<nono.length; ++i) {
        if (nono[i].toLowerCase() == "=") {
            if (o !== 0) {
                newnono = newnono + " ";
                o = 0;
            }
            newnono = newnono + "=";
        }
        else {
            newnono = newnono + ")";
            ++o;
        }
    }
    document.getElementById('binary').value = newnono;
}

function fhspeak_to_fhspeak() {
    document.getElementById('fhspeak').value = fhspeak.encode(document.getElementById('fhspeak').value);
}

function qbf_to_qbf() {
    document.getElementById('qbf').value = Symbolfuck.encode(document.getElementById('qbf').value);
}

function convert_all() {
    try { str_to_reverse(); }
    catch (e) { null; }
    try { str_to_eb64(); }
    catch (e) { null; }
    try { str_to_b64(); }
    catch (e) { null; }
    try { str_to_fhspeak(); }
    catch (e) { null; }
    try { str_to_qbf(); }
    catch (e) { null; }
    try { str_to_goomy(); }
    catch (e) { null; }
    try { str_to_binary(); }
    catch (e) { null; }
}
