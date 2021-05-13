$(document).ready(function(){
    var key = "pk.eyJ1IjoieGFuZGVyMTIzNDU2Nzg5IiwiYSI6ImNra282cGNjaDBucjkyeHJ3MTU3cWMxOGEifQ.QosXrSzp3JpIbd0186_snQ";
    
    function getGeoCodingLink(place){
        return `https://api.mapbox.com/geocoding/v5/mapbox.places/${place}.json?access_token=${key}`;
    }
    
});