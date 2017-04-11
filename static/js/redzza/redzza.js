// https://developer.mozilla.org/en-US/docs/Web/API

/* Body variables */
var all = document.getElementById('all');

(function () {
  /* form-login actions, if it's true redirect to home, if isn't rendering error */
  $('#form-login').submit(function (e) {
    e.preventDefault();
    var form = $(this);
    $.post(form.attr('data-url'), form.serialize(), function (response, status, jqXHR) {
      if (response.success) {
        window.location.href = response.url;
      }else{
        document.getElementById('login-response').innerHTML = `<p class="danger-alert">${response.errors.__all__[0]}</p>`
      }
    });
  });

  /* form-signup actions */
  $('#form-signup').submit(function (e) {
    e.preventDefault();
    var response =  document.getElementById('signup-response');
    if(document.getElementById('terms').checked) {
      var url = $('#signup-input').attr('data-url') + "?email=" + $('#signup-input').val();
      $.get(url, function (data) {
        if (data.is_taken) {
          response.innerHTML = `<p class="danger-alert">Este correo ya tiene una cuenta asociada, prueba iniciando sesion.</p>`;
        }else{
          sessionStorage.setItem('email', $('#signup-input').val()); // Save email in sessionStorage
          window.location.href = $('#form-signup').attr('data-url'); // Redirecting to step1
        }
      });
    }else{
      response.innerHTML = `<p class="danger-alert">Para registrarte debes aceptar nuestros terminos y condiciones.</p>`;
    }
  });

  /* Save info in sessionStorage and Redirect to step2 */
  $('#form-profile-info').submit(function (e) {
    e.preventDefault();
    var password1 = document.getElementById('form-profile-info')[2].value; // Password
    var password2 = document.getElementById('form-profile-info')[3].value; // Retype Password
    if (password1 == password2) {
      sessionStorage.setItem('name', document.getElementById('form-profile-info')[0].value); // Name
      sessionStorage.setItem('lastname', document.getElementById('form-profile-info')[1].value); // Lastname
      sessionStorage.setItem('password', document.getElementById('form-profile-info')[2].value); // Password
      sessionStorage.setItem('place', document.getElementById('form-profile-info')[4].value); // Place
      window.location.href = $('#form-profile-info').attr('data-url'); // Redirecting to step1
    }else {
      document.getElementById('response').innerHTML = `<p class="danger-alert">Las contraseñas no coinciden</p>`;
    }
  });

  /* == Step 2 */
  if($('#categories').length){
    $.get($('#categories').attr('data-url'), function (json) {
      console.log(json);
      document.getElementById('categories').innerHTML  = JSON.parse(json).map(function (categorie, index) {
        return (`<div class="categorie">
          <input type="checkbox" value="${categorie.pk}">
          <p>${categorie.fields.name}</p>
        </div>`);
      }).join('');
    });
  }

  // Categorias que tengo
  $('#form-profile-info2').submit(function (e) {
    // faltan validaciones 0 categorias o mas del numero total
    e.preventDefault();
    var aux = new Array();
    $('#form-profile-info2').find('input[type="checkbox"]:checked').each(function (checkbox) {
      aux.push({pk:$(this).attr('value')});
    });
    sessionStorage.setItem('busco', JSON.stringify(aux));
    window.location.href = $('#form-profile-info2').attr('data-url');
  });

  // categorias que busco
  $('#form-profile-info3').submit(function (e) {
    // faltan validaciones 0 categorias o mas del numero total
    e.preventDefault();
    var aux = new Array();
    $('#form-profile-info3').find('input[type="checkbox"]:checked').each(function (checkbox) {
      aux.push({pk:$(this).attr('value')});
    });
    sessionStorage.setItem('tengo', JSON.stringify(aux));
    csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    // csrf_token = $("input[name:'csrfmiddlewaretoken']").val();
    $.ajax({
      type: "POST",
      url: $(this).attr('data-url'),
      data: { name : sessionStorage.getItem('name'), lastname : sessionStorage.getItem('lastname'), password: sessionStorage.getItem('password'), place: sessionStorage.getItem('place'), busco: sessionStorage.getItem('busco'), tengo: sessionStorage.getItem('tengo'), csrfmiddlewaretoken: csrf_token},
      success: function (response) {
        if (response.success) {
          window.location.href = response.url;
        }else {
          console.log("Paila");
        }
      }
    });
    // terminar proceso
  });

})();

$(document).ready(function() {
  // Select2
  $(".js-example-basic-single").select2({
    language: "es",
    minimumInputLength: 2,
    tags: [],
    ajax: {
      url: $('#places').attr('data-url'),
      dataType: 'JSON',
      type: "GET",
      quietMillis: 50,
      data: function (term) {
        return {
          term: term
        };
      }
    }
  });
});
  // /Select2


  /* Landing functions */
  function notMember() {
    closeModal('modal-login');
    getModal('modal-signup');
  }

  /* === Modal actions
  * Display de modal by id */
  function getModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = 'block';
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }
  }

  /* Hidde modal by id */
  function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
  }
