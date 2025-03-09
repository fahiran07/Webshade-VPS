function login_account() {
	show_spinner();

	// Get phone and password values from input fields
	var phone = document.getElementById("phone").value;
	var password = document.getElementById("password").value;

	if (phone && password) {
		// Send login request to the server
		fetch("/api/login/", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
			body: JSON.stringify({ phone: phone, password: password }),
		})
			.then((response) => response.json())
			.then((data) => {
				hide_spinner();
				if (data.error == 0) {
					show_toast_message(data.message, true);
					setTimeout(() => {
						show_spinner();
						location.href = "/connect";
					}, 1200);
				} else {
					show_toast_message(data.message, false);
				}
			});
	} else {
		hide_spinner();
		show_toast_message("Please fill in both phone and password fields.", false);
	}
}
