'use strict';

var PokemonGO = require('pokemon-go-node-api');
//var s2 = require('s2geometry-node');
// using var so you can login with multiple users


var a = new PokemonGO.Pokeio();

var fs = require('fs');
var util = require('./util');
var config = fs.readFileSync('config.json');
config = JSON.parse(config);

//Set environment variables or replace placeholder text
var location = {
    type: 'name',
    name: config.loc
};


var username = config.username;
var password = config.password;
var provider = config.auth;

var hb = function(loc) {
    a.SetLocation({type:'coords', coords:{latitude: loc.lat, longitude: loc.lng, altitude:0}}, function(err, cord){
        a.Heartbeat(function(err, hb){
            if(err){
                console.log(err);
            }
            for (var i = hb.cells.length -1; i>=0; i--) {
                if (hb.cells[i].WildPokemon[0]) {
                    for (var j = 0; j < hb.cells[i].WildPokemon.length; j++) {
                        var pokemon = a.pokemonlist[parseInt(hb.cells[i].WildPokemon[j].pokemon.PokemonId)];
                        console.log(pokemon.name +' at '+hb.cells[i].WildPokemon[j].Latitude+', '+hb.cells[i].WildPokemon[j].Longitude);
                        var time = new Date((new Date()).getTime() + hb.cells[i].WildPokemon[j].TimeTillHiddenMs);
                        console.log('Hides at: '+ time.toLocaleTimeString());
                    }
                }
            }
        });
    });
}

a.init(username, password, location, provider, function(err) {
    if (err) throw err;

    console.log('1[i] Current location: ' + a.playerInfo.locationName);
    console.log('1[i] lat/long/alt: : ' + a.playerInfo.latitude + ' ' + a.playerInfo.longitude + ' ' + a.playerInfo.altitude);

    var spiral = util.generate_spiral(a.playerInfo.latitude, a.playerInfo.longitude, 0.0015, 16);

    console.log(spiral);
    var index =0;

    setInterval(function() {
        if (index < spiral.length) {
            hb(spiral[index]);
            index++;
        } else {
            process.exit();
        }
    }, 2000);
    


    // a.Heartbeat(function(err, hb){
    //     if(err){
    //         console.log(err);
    //     }
    //     for (var i = hb.cells.length -1; i>=0; i--) {
    //         if (hb.cells[i].WildPokemon[0]) {
    //             for (var j = 0; j < hb.cells[i].WildPokemon.length; j++) {
    //                 var pokemon = a.pokemonlist[parseInt(hb.cells[i].WildPokemon[j].pokemon.PokemonId)];
    //                 console.log(pokemon.name +' at '+hb.cells[i].WildPokemon[j].Latitude+', '+hb.cells[i].WildPokemon[j].Longitude);
    //                 var time = new Date((new Date()).getTime() + hb.cells[i].WildPokemon[j].TimeTillHiddenMs);
    //                 console.log('Hides at: '+ time.toLocaleTimeString());
    //             }
    //         }
    //     }
    // });
});





