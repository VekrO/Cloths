let linkProduct = document.querySelectorAll('#link-product');

linkProduct.forEach( element => {
    element.addEventListener('click', ()=>{
        let productName= element.childNodes[1].textContent.replace('>', '').toLocaleLowerCase().replace('  ', '').normalize('NFD').replace(/[\u0300-\u036f]/g, '');

        let url = new URL(window.location.href);
        var productParams = url.searchParams.get("product");
        if(productParams.length == 0 || productParams == ''){
            location.href = window.location.href + productName
        }else{
            location.href = window.location.href.replace(productParams, productName)
        }
        
    })
})
