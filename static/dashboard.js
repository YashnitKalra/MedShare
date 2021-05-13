function getCsrfToken(){
    return $('[name=csrfmiddlewaretoken]')[0].value;
}

$("#searchProductButton").click(()=>{
    var product = $("#searchProductName").val();
    var sortBy = $("#sortBy").val();
    if(product.length<3) alert("Enter at least 3 letters");
    else{
        $.ajax({
            url: "searchProducts",
            type: "GET",
            data: {product: product, sortBy: sortBy},
            success: (result)=>{
                result = JSON.parse(result);
                $("#products").empty();
                if(result['found']){
                    var products = result['products'];
                    var j;
                    for(var i=0;i<products.length;i++){
                        j = products[i][5];
                        $("#products").append(`<div class="row font-sm-responsive" id="row${j}"></div>`);
                        $(`#row${j}`).append(
                            `<div class="col bg-transparent-light m-2 text-center py-2 rounded">`+
                            `<h5 class="heading font-md-responsive">${products[i][0].toUpperCase()}</h5>`+
                            `<div>${products[i][1]}</div><hr class="my-1">`+
                            `<div>Expire in <span class="font-weight-bold">${products[i][2]} days</span>.`+
                            `<div>${products[i][3]} (Approx <span class="font-weight-bold">${products[i][4]} km</span> away)</div>`+
                            `<label>(Available: <span class="font-weight-bold" id="remaining${j}">${products[i][6]}</span>) Quantity:</label>`+
                            `<input type="number" value=1 min=1 max=${parseInt(product[i][6])} class="mx-2" id="quantity${j}">`+
                            `<button type="button" class="btn btn-sm btn-info font-sm-responsive requestButton mt-1" id="${j}">Request</button>`
                        );
                    }
                    addRequestButtonFunctionality()
                }else $("#products").append("<h4 class='text-danger text-center bg-transparent-light'>Product not Available</h4>");
            }
        });
    }
});

$("#donateButton").click(()=>{
    var productName = $("#productName").val();
    var description = $("#description").val();
    var expiryDate = $("#expiryDate").val();
    var quantity = parseInt($("#productQuantity").val());
    if(productName.length==0) alert("Enter Product Name");
    else if(!(quantity>=1)) alert("Minimum Quantity Should be 1");
    else if(expiryDate.length==0) alert("Enter Expiry Date");
    else{
        $.ajax({
            url: "uploadMedicinalProduct",
            type: "POST",
            data: {productName: productName, description: description, expiryDate: expiryDate, quantity: quantity, csrfmiddlewaretoken: getCsrfToken()},
            success: function(result){
                result = JSON.parse(result);
                if(result['error']) alert(result['message']);
                else{
                    alert("Thank You for Donating");
                    $("#donateModal").modal("toggle");
                }
            }
        });
    }
});

function addRequestButtonFunctionality(){
    $(".requestButton").click(function(){
        var quantity = parseInt($(`#quantity${this.id}`).val());
        if(!(quantity>=1)) alert("Minimum Quantity Should be 1");
        else{
            if(confirm("Are you sure?")){
                $.ajax({
                    url: "requestProduct",
                    type: "POST",
                    data: {csrfmiddlewaretoken: getCsrfToken(), id: this.id, quantity: quantity},
                    success: (result) => {
                        result = JSON.parse(result);
                        if(result['error']) alert(result['message']);
                        else{
                            alert("Request Sent");
                            console.log(result);
                            if(result['remaining']==0)
                                $(`#row${this.id}`).remove();
                            else
                                $(`#remaining${this.id}`).text(result['remaining']);
                            $("#count").text(parseInt($("#count").text())-1);
                        }
                    }
                });
            }
        }
    });
}