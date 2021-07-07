let places = document.getElementById("places")
let club_points = Number.parseInt(document.getElementById("club-points").value)
let competition_places = Number.parseInt(document.getElementById("competition-places").value)
let max_booking_places = Number.parseInt(document.getElementById("max-booking-places").value)
let button_submit_form = document.getElementById("submit-form")
let error_message = document.getElementById("error-message")


places.addEventListener("input", function(e) {
    let places_required = e.target.value
    button_submit_form.disabled = true
    if (places_required > competition_places) {
        error_message.innerHTML = "Number of places required is greater than competition's number of places : " + competition_places
    } else if (places_required > club_points) {
        error_message.innerHTML = "Number of places required is greater than club's points : " + club_points
    } else if (places_required > max_booking_places) {
        error_message.innerHTML = "Number of places required is greater than maximum places authorized : " + max_booking_places
    } else if (places_required < 1) {
        error_message.innerHTML = "Number of places required is less than 1"
    } else {
        error_message.innerHTML = ""
        button_submit_form.disabled = false
    }
})
