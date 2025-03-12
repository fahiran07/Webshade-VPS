function acceptRequest(connectId) {
	console.log(connectId);

	show_spinner();
	fetch("/admin-panel-124432/api/accept-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: connectId }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				show_toast_message("Request Accepted Successfully", true);
				document.getElementById("connect-" + connectId);
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function rejectRequest(connectId) {
	fetch("/admin-panel-124432/api/reject-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: connectId }),
	})
		.then((response) => response.json())
		.then((data) => {
			if (!data.error) {
				show_toast_message("Request Rejected Successfully", true);
				document.getElementById("whatsapp-" + connectId).remove();
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function showCodeBox(connectId) {
	currentConnectId = connectId;
	document.getElementById("code_box").classList.remove("d-none");
}

function hideCodeBox() {
	document.getElementById("code_box").classList.add("d-none");
}

function sendCode() {
	let code = document.getElementById("code").value;
	show_spinner();
	fetch("/admin-panel-124432/api/send-code/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: currentConnectId, code: code }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				document.getElementById("code_box").classList.add("d-none");
				show_toast_message(data.message, true);
			} else {
				show_toast_message(data.message, false);
			}
		});
}
function update_server_status(updating_status) {
	show_spinner();
	fetch("/admin-panel-124432/api/update-server-status/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({
			updating_status: updating_status,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				document.getElementById("server-status").classList.toggle("text-danger");
				document.getElementById("server-status").classList.toggle("text-success");
				document.getElementById("server-status").innerText = updating_status;
				show_toast_message(data.message, true);
			} else {
				show_toast_message(data.message, false);
			}
		});
}
