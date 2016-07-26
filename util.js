module.exports.generate_spiral = function(starting_lat, starting_lng, step_size, step_limit) {
    var coords = [{'lat': starting_lat, 'lng':starting_lng}];
    var steps = 1;
    var x = 0;
    var y = 0;
    var d = 1;
    var m = 1;
    var rlow = 0.0;
    var rhigh = 0.0005;

    while (steps < step_limit) {
        while (2*x*d < m && steps < step_limit) {
            x = x + d;
            steps = steps +1;
            var lat = x * step_size + starting_lat + Math.random() * (rhigh-rlow) + rlow;
            var lng = y * step_size + starting_lng + Math.random() * (rhigh-rlow) + rlow;
            coords.push({'lat': lat, 'lng':lng});
        }
        while (2*y*d < m && steps < step_limit) {
            y = y + d;
            steps = steps +1;
            var lat = x * step_size + starting_lat + Math.random() * (rhigh-rlow) + rlow;
            var lng = y * step_size + starting_lng + Math.random() * (rhigh-rlow) + rlow;
            coords.push({'lat': lat, 'lng':lng});
        }

        d = -1 * d;
        m = m + 1;
    }
    return coords;
}
