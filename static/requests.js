function getCsrfToken(){
    return $('[name=csrfmiddlewaretoken]')[0].value;
}

$(".withdrawRequestButton").click(function(){
    var id = this.id.split("_")[1];
    if(confirm("Are you sure?")){
        $.ajax({
            url: "withdrawRequest",
            type: "POST",
            data: {id: id, csrfmiddlewaretoken: getCsrfToken()},
            success: (result)=>{
                result = JSON.parse(result);
                if(result['error']) alert(result['message']);
                else{
                    alert("Request Withdrawn");
                    $(this).parent().parent().remove();
                }
            }
        });
    }
});

$(".acceptRequestButton").click(function(){
    var id = this.id.split("_")[1];
    if(confirm("Are you sure?")){
        $.ajax({
            url: "acceptRequest",
            type: "POST",
            data: {id:id, csrfmiddlewaretoken: getCsrfToken()},
            success: (result)=>{
                result = JSON.parse(result);
                if(result['error']) alert(result['message']);
                else{
                    alert("Request Accepted");
                    var parent = $(this).parent();
                    $(parent).empty();
                    $(parent).append(`<button class="btn btn-sm btn-outline-info confirmRequestButton" id="confirm_${id}">Confirm Exchange</button>`);
                }
            }
        });
    }
});

$(".rejectRequestButton").click(function(){
    var id = this.id.split("_")[1];
    if(confirm("Are you sure?")){
        $.ajax({
            url: "rejectRequest",
            type: "POST",
            data: {id:id, csrfmiddlewaretoken: getCsrfToken()},
            success: (result)=>{
                result = JSON.parse(result);
                if(result['error']) alert(result['message']);
                else{
                    alert("Request Rejected");
                    var parent = $(this).parent();
                    $(parent).empty();
                    $(parent).append('<span class="text-danger">REJECTED</span>');
                }
            }
        });
    }
});

$(".cancelRequestButton").click(function(){
    var id = this.id.split("_")[1];
    if(confirm("Your request count won't be incremented, Are you sure?")){
        $.ajax({
            url: "cancelRequest",
            type: "POST",
            data: {id:id, csrfmiddlewaretoken: getCsrfToken()},
            success: (result)=>{
                result = JSON.parse(result);
                if(result['error']) alert(result['message']);
                else{
                    alert("Request Cancelled");
                    var parent = $(this).parent();
                    $(parent).empty();
                    $(parent).append('-');
                    $(`#status_${id}`).removeClass("text-success").addClass("text-danger").empty().append("Unsuccessful");
                }
            }
        });
    }
});

var otpEnc, ID;

$(".confirmRequestButton").click(function(){
    var id = this.id.split("_")[1];
    if(confirm("Are you with the receiver?")){
        $("#exchangeModal").modal("show");
    }
    $.ajax({
        url: "sendOtpToReceiver",
        type: "POST",
        data: {id:id, csrfmiddlewaretoken:getCsrfToken()},
        success: (result)=>{
            result = JSON.parse(result);
            if(result['error']) alert(result['message']);
            else{
                otpEnc = result['otp'];
                ID = id;
            }
        }
    });
});

$("#submitOtpButton").click(function(){
    var otp = $("#otp").val();
    if(otp.length!=6) alert("Invalid OTP");
    else{
        $.ajax({
            url: "confirmExchange",
            type: "POST",
            data: {id:ID, otp:otp, otp2:otpEnc, csrfmiddlewaretoken:getCsrfToken()},
            success: (result)=>{
                result = JSON.parse(result);
                if(result['error']) alert(result['message']);
                else{
                    var parent = $(`#confirm_${ID}`).parent();
                    $(parent).empty();
                    $(parent).append(`<span class="font-weight-bold text-success">SUCCESSFUL</span>`);
                    $("#exchangeModal").modal("hide");
                }
            }
        });
    }
});