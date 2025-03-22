function release_payment() {
	show_spinner();
	fetch("/admin-panel/api/release-payment/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({}),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				show_toast_message(data.message, true);
			} else {
				show_toast_message(data.message, false);
			}
		});
}
