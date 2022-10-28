let products = document.querySelectorAll('.esseprodutotem');
let formAdd = document.querySelector('.form-add');

// Stopping form submit.

formAdd.addEventListener('submit', (e)=>{

    e.preventDefault();
    let soma = 0
    // Code ...
    products.forEach((element)=> {
        soma += parseInt(element.value)
    })

    if(soma == 0){
        Swal.fire( "Oops" ,  "Você precisa adicionar algo!" ,  "error");
    }else{

        products.forEach(element => {
            if(element.value != 0){
                $.ajax({
                    type: "POST",
                    url: "/meus_pacotes/" + document.querySelector('.userInfo').dataset.userid + '/',
                    data: {
                        'product_id': document.querySelector('.addButton').dataset.id,
                        'product_qnt': element.value,
                        'product_size': element.dataset.size,
                        'loja_id': document.querySelector('.addButton').dataset.lojaid,
                        'user_id': document.querySelector('.userInfo').dataset.userid,
                    },
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    dataType: "dataType",
                    success: function (response){
                        console.log('sucesso');
                    },
                });
            }
        })

        Swal.fire(
            'Produto Adicionado!',
            'Vá ao carrinho!',
            'success'
            ).then(
                data=>{
                    if(data.isConfirmed){
                        document.querySelector('#mod').style.left = '-100%';
                        products.forEach(e=>{
                            e.value = 0;
                    }
                )
                }
            }
        )
    }

})

function openModal(element){
    document.querySelector(`#${element}`).style.left = '10%';
}

function closeModal(element){
    document.querySelector(`#${element}`).style.left = '-100%';
}

// Pegar CSRF Token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/*

*/