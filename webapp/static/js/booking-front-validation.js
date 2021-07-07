let places = document.getElementById("places")
let club_points = Number.parseInt(document.getElementById("club-points").value)
let competition_places = Number.parseInt(document.getElementById("competition-places").value)
let error_message = document.getElementById("error-message")

places.addEventListener("input", function(e) {
    let places_required = e.target.value
    if (places_required > competition_places) {
        error_message.innerHTML = "Number of places required is greater than competition's number of places : " + competition_places
    } else if (places_required > club_points) {
        error_message.innerHTML = "Number of places required is greater than club's points : " + club_points
    } else {
        error_message.innerHTML = ""
    }
})
