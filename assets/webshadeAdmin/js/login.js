function superuser_login() {
	show_spinner();
	let username = document.getElementById("username").value;
	let password = document.getElementById("password").value;
	show_spinner();
	fetch("/admin-panel/api/login/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ username: username, password: password }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				show_toast_message(data.message, true);
				location.href = "/admin-panel/";
			} else {
				show_toast_message(data.message, false);
			}
		});
}
