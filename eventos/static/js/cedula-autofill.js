var fnf = document.getElementById("id_cedula");
fnf.addEventListener('keyup', function(evt){
    var n = parseInt(this.value.replace(".",""),11);
    fnf.value = n.toString().replace(/\B(?=(\d{3})+(?!\d))/g,".");
}, false);