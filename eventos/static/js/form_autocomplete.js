/*
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
*/
function form_autocomplete(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/

  var currentFocus;
   /*execute a function when someone writes in the text field:*/
  var val = inp.value;
  /*close any already open lists of autocompleted values*/

  if (!val) { return false;}
  currentFocus = -1;
  /*create a DIV element that will contain the items (values):*/

  a = document.createElement("DIV");
  a.setAttribute("id", inp.id + "autocomplete-list");
  a.setAttribute("class", "autocomplete-items panel");
  val_index = 0 ? inp.id == 'invi_persona' : 1;
  /*append the DIV element as a child of the autocomplete container:*/
  /*for each item in the array...*/
  for (i = 0; i < arr[0].length; i++) {
    /*check if the item starts with the same letters as the text field value:*/
      /*create a DIV element for each matching element:*/
      b = document.createElement("DIV");
      /*make the matching letters bold:*/
      if(inp.id == 'invi_persona') {
          b.innerHTML = "<p>"+arr[0][i][0]+" - "+arr[0][i][1]+"</p>";
      }
      else{if(inp.id == 'invi_cedula') {
            b.innerHTML = "<p>"+arr[0][i][0]+" - "+arr[0][i][1]+"</p>";
      }
      else{
          b.innerHTML = "<a href='/e/"+arr[1]+"/p/"+arr[0][i][1]+"/'> "+arr[0][i][0]+"</a>";
      }}
      b.classList.add('opciones');
      b.classList.add('li');
      /*insert a input field that will hold the current array item's value:*/
      b.innerHTML += "<input type='hidden' value='" + arr[0][i][0] +" - "+arr[0][i][1]+"'>";
      if(inp.id == 'invi_persona'){
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field and close lists*/
              var data = this.getElementsByTagName("input")[0].value.split(' - ')
              inp.value = data[0];
              document.getElementById('invi_cedula').value = data[1]
              closeAllLists();
              checkForm();
          });
      }
      else{if(inp.id == 'invi_cedula'){
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field and close lists*/
              var data = this.getElementsByTagName("input")[0].value.split(' - ')
              inp.value = data[1];
              document.getElementById('invi_persona').value = data[0]
              closeAllLists();
              checkForm();
          });
      }}
      a.appendChild(b);
  }
  closeAllLists();
  inp.parentNode.insertBefore(a, inp.nextSibling);
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
  var x = document.getElementById(this.id + "autocomplete-list");
  if (x) x = x.getElementsByTagName("div");
  if (e.keyCode == 40) {
    /*If the arrow DOWN key is pressed,
    increase the currentFocus variable:*/
    currentFocus++;
    /*and and make the current item more visible:*/
    addActive(x);
  } else if (e.keyCode == 38) { //up
    /*If the arrow UP key is pressed,
    decrease the currentFocus variable:*/
    currentFocus--;
    /*and and make the current item more visible:*/
    addActive(x);
  } else if (e.keyCode == 13) {
    /*If the ENTER key is pressed, prevent the form from being submitted,*/
    e.preventDefault();
    if (currentFocus > -1) {
      /*and simulate a click on the "active" item:*/
      if (x) x[currentFocus].click();
    }
  }
});
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
      x[i].parentNode.removeChild(x[i]);
    }

  }
}
/*execute a function when someone clicks in the document:*/
document.addEventListener("click", function (e) {
    closeAllLists(e.target);
});
}
