var key = "pk.eyJ1IjoieGFuZGVyMTIzNDU2Nzg5IiwiYSI6ImNra282cGNjaDBucjkyeHJ3MTU3cWMxOGEifQ.QosXrSzp3JpIbd0186_snQ&types=locality&limit=10";
var places, coordinates;
var otpEnc, email;
var emailVerified = false, usernameVerified = false, areaVerified = false;

document.getElementById("registrationForm").reset();

function getGeoCodingLink(place){
    return `https://api.mapbox.com/geocoding/v5/mapbox.places/${place}.json?access_token=${key}`;
}

function isValidEmail(email){
    return email.search(/^.+@.+\..{2,}$/)!=-1;
}

function getCsrfToken(){
    return $('[name=csrfmiddlewaretoken]')[0].value;
}

$("#area").keyup(function(){
    areaVerified = false;
});

$("#findAreaButton").click(function(){
    var val = $("#area").val();
    if(val.length>2){
        val = val.replace(" ","+");
        var link = getGeoCodingLink(val);
        places = []; coordinates = [];
        $.ajax({
            url: link,
            success: function(result){
                $("#areasList").empty();
                if(result['features'].length>0){
                    for(index in result['features']){
                        coordinates.push(result['features'][index]['geometry']['coordinates']);
                        places.push(result['features'][index]['place_name'])
                        $("#areasList").append(`<div class="form-check mb-2"><label class="form-check-label"><input type="radio" class="form-check-input" value=${index} name="radioArea">${result['features'][index]['place_name']}</label></div>`);
                    }
                    $("input[type=radio][name=radioArea]").change(function(){
                        var i = $(this).val();
                        $("#area, #area2").val(places[i]);
                        $("#lat").val(coordinates[i][1]);
                        $("#lon").val(coordinates[i][0]);
                        areaVerified = true;
                    });
                }else{
                    $("#areasList").append("<h4>Area not found</h4>");
                }
                $("#areas").modal();
            }
        });
    }else alert("Please Enter at least 3 characters");
});

$("#enterEmailButton").click(function(){
    $("#email2, #sendOtpButton").removeClass("d-none").addClass("d-block");
    $("#otp, #otpVerifyButton").removeClass("d-block").addClass("d-none");
    $("#email2, #otp").val("");
    $("#emailModal").modal();
    $("#sendOtpButton, #otpVerifyButton").prop("readonly",false);
    otpEnc = null;
    email = null;
});

$("#sendOtpButton").click(function(){
    email = $("#email2").val();
    $("#sendOtpButton").prop("readonly",true);
    if(isValidEmail(email)){
        $.ajax({
            url: "sendOtp",
            type: "POST",
            data: {email: email, csrfmiddlewaretoken: getCsrfToken()},
            success: function(result){
                result = JSON.parse(result);
                if(result["error"]) alert(result["message"]);
                else{
                    $("#otp, #otpVerifyButton").removeClass("d-none").addClass("d-block");
                    $("#email2, #sendOtpButton").removeClass("d-block").addClass("d-none");
                    otpEnc = result["otp"];
                }
            }
        });
    }else alert("Invalid Email");
});

$("#otpVerifyButton").click(function(){
    $("#otpVerifyButton").prop("readonly",true);
    var otp = $("#otp").val();
    $.ajax({
        url: "verifyOtp",
        type: "POST",
        data: {otp: otp, otp2: otpEnc, csrfmiddlewaretoken: getCsrfToken()},
        success: function(result){
            result = JSON.parse(result);
            if(result["error"]==true){
                alert("Invalid OTP");
                $("#otpVerifyButton").prop("readonly",false);
            }else{
                $("#email1").val(email);
                emailVerified = true;
                $("#emailModal").modal("toggle");
            }
        }
    });
});

$("#verifyUsernameButton").click(function(){
    var username = $("#username").val();
    $.ajax({
        url: 'verifyUsername',
        type: 'POST',
        data: {username: username, csrfmiddlewaretoken: getCsrfToken()},
        success: function(result){
            result = JSON.parse(result);
            if(result['error']) alert(result['message']);
            else{
                usernameVerified = true;
                alert("Username Verified");
                $("#username").prop('readonly',true);
            }
        }
    });
});

function verifyDetails(){
    var pass1 = $("#password1").val(), pass2 = $("#password2").val();
    if(pass1!=pass2){alert("Password Not Matched"); return false;}
    else if(!usernameVerified){alert("Please verify username"); return false;}
    else if(!emailVerified){alert("Please verify Email"); return false;}
    else if(!areaVerified){alert("Please verify area"); return false;}
    usernameVerified = false; emailVerified = false; areaVerified = false;
    return true;
}