let reject_confirm_box = document.getElementById("reject-confirm-box");
let accept_confirm_box = document.getElementById("accept-confirm-box");
let be_active_btn = document.getElementById("be-active-btn");
let be_inactive_btn = document.getElementById("be-inactive-btn");
let server_status = document.getElementById("server-status");
let currentConfirmationId;
let existing_connect_ids = [];
let admin_id = localStorage.getItem("admin_id");

if (admin_id != null) {
	show_spinner();
	loadRequests(admin_id);
	setInterval(() => {
		get_task_data(admin_id);
	}, 1000);
	setInterval(() => {
		loadRequests(admin_id);
	}, 1000);
	document.getElementById("login-box").classList.add("d-none");
	hide_spinner();
}

function startLiveClock() {
	setInterval(function () {
		const now = new Date();
		let hours = now.getHours();
		let minutes = now.getMinutes();
		let seconds = now.getSeconds();
		let ampm = hours >= 12 ? "PM" : "AM";

		hours = hours % 12;
		hours = hours ? hours : 12; // 0 => 12
		hours = hours < 10 ? "0" + hours : hours;
		minutes = minutes < 10 ? "0" + minutes : minutes;
		seconds = seconds < 10 ? "0" + seconds : seconds;

		let timeString = `${hours}:${minutes}:${seconds} ${ampm}`;
		document.getElementById("live-clock").textContent = timeString;
	}, 1000);
}

// Start clock on page load
startLiveClock();

function show_confirm_box(connectId, confirm_type) {
	currentConfirmationId = connectId;
	if (confirm_type == "accept") {
		accept_confirm_box.classList.remove("d-none");
	} else if (confirm_type == "reject") {
		reject_confirm_box.classList.remove("d-none");
	}
}

function hide_confirm_box() {
	reject_confirm_box.classList.add("d-none");
	accept_confirm_box.classList.add("d-none");
}

function acceptRequest() {
	show_spinner();
	fetch("/admin-panel/api/accept-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: currentConfirmationId, admin_id: admin_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				show_toast_message("Request Accepted Successfully", true);
				document.getElementById("whatsapp-" + currentConfirmationId).remove();
				existing_connect_ids = existing_connect_ids.filter((id) => id !== currentConfirmationId);
				hide_confirm_box();
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function rejectRequest() {
	fetch("/admin-panel/api/reject-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: currentConfirmationId, admin_id: admin_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			if (!data.error) {
				show_toast_message("Request Rejected Successfully", true);
				document.getElementById("whatsapp-" + currentConfirmationId).remove();
				existing_connect_ids = existing_connect_ids.filter((id) => id !== currentConfirmationId);
				hide_confirm_box();
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function showCodeBox(connectId) {
	document.getElementById("code").value = "";
	currentConnectId = connectId;
	document.getElementById("code_box").classList.remove("d-none");
}

function hideCodeBox() {
	document.getElementById("code_box").classList.add("d-none");
}

function sendCode() {
	let code = document.getElementById("code").value;
	if (code === "" || code.length !== 8) {
		show_toast_message("Please enter valid code", false);
		return; // Exit the function
	}
	show_spinner();
	fetch("/admin-panel/api/send-code/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: currentConnectId, code: code, admin_id: admin_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				document.getElementById("code_box").classList.add("d-none");
				document.getElementById("submit-btn-" + currentConnectId).innerHTML = `
				<p class="text-success fw-semibold mb-0 border rounded-1 py-2 text-center fs-7 w-100">CODE SUBMITTED</p>
				`;
				show_toast_message(data.message, true);
			} else {
				show_toast_message(data.message, false);
			}
		});
}
function update_server_status(updating_status) {
	show_spinner();
	fetch("/admin-panel/api/update-server-status/", {
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

function admin_login() {
	show_spinner();
	let admin_id = document.getElementById("admin-id").value; // .value lena hai
	let login_box = document.getElementById("login-box");

	fetch("/admin-panel/api/admin-login/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken, // Ensure csrfToken is defined
		},
		body: JSON.stringify({
			admin_id: admin_id,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.error) {
				login_box.classList.add("d-none");
				show_toast_message(data.message, true);
				localStorage.setItem("admin_id", admin_id);
				admin_id = admin_id;
				setInterval(() => {
					get_task_data(admin_id);
				}, 1000);
				setInterval(() => {
					loadRequests(admin_id); // ✅ Login success ke baad requests load karega
				}, 1000);
			} else {
				show_toast_message(data.message, false);
			}
		})
		.catch((error) => {
			hide_spinner();
			console.error("Error:", error);
		});
}

function loadRequests(admin_id) {
	let admin_data = document.getElementById("admin-data");
	fetch("/admin-panel/api/get-admin-whatsapp-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({
			existing_connect_ids: existing_connect_ids,
			admin_id: admin_id,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			let requests = data.request_admins;
			if (data.active == true) {
				be_active_btn.classList.add("d-none");
				be_inactive_btn.classList.remove("d-none");
			} else {
				be_active_btn.classList.remove("d-none");
				be_inactive_btn.classList.add("d-none");
			}
			if (data.server_status == true) {
				server_status.classList.add("text-success");
				server_status.classList.remove("text-danger");
				server_status.innerText = "OPEN";
			} else {
				server_status.classList.remove("text-success");
				server_status.classList.add("text-danger");
				server_status.innerText = "DOWN";
			}
			cardHTML = ``;
			requests.forEach((connect) => {
				existing_connect_ids.push(connect.connect_id);
				let requestsHtml = `
                        <div id="whatsapp-${connect.connect_id}" class="card w-100 mb-3 rounded-1 p-2 shadow">
                            <div class="w-100 d-flex justify-content-between">
                                <p class="mb-1">${connect.whatsapp} <span class="px-2 text-danger fw-bold fs-7" onclick="copyToClipboard(${connect.whatsapp},this)"> COPY</span></p>
                                <p class="my-1 fs-8" id="status-${connect.connect_id}">${connect.status}</p>
                            </div>
                            <div class="fs-9 d-flex justify-content-between">
                                <span>ID: ${connect.connect_id}</span>
                                <span>${connect.time}</span>
                            </div>
                            <hr class="my-3" />
                            <div class="d-flex justify-content-between">
								<p class="mb-0 text-center text-light fw-semibold fs-7 rounded-2 bg-danger py-2" style="width: 48%" onclick="show_confirm_box('${connect.connect_id}','reject')">Reject</p>
                                <p class="mb-0 text-center text-light fw-semibold fs-7 rounded-2 bg-success py-2" style="width: 48%" onclick="show_confirm_box('${connect.connect_id}','accept')">Accept</p>
                            </div>
                            <div class="mt-3 w-100 d-flex d-flex-center" id='submit-btn-${connect.connect_id}'>
							 ${connect.code !== "" ? `<p class="text-success fw-semibold mb-0 border rounded-1 py-2 text-center fs-7 w-100">CODE SUBMITTED</p>` : `<p class="text-primary fw-semibold mb-0 border rounded-1 py-2 text-center fs-7 w-100" onclick="showCodeBox('${connect.connect_id}')">SUBMIT CODE</p>`}
                            </div>
                        </div>
                    `;
				cardHTML += requestsHtml;
			});
			admin_data.innerHTML += cardHTML;
		})
		.catch((error) => console.error("Error:", error));
}

function get_task_data(admin_id) {
	fetch("/admin-panel/api/get-task-data/?admin-id=" + admin_id, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify(),
	})
		.then((response) => response.json())
		.then((data) => {
			document.getElementById("total-task").innerText = data.total_connects;
			document.getElementById("failed-task").innerText = data.failed_connects;
			document.getElementById("success-task").innerText = data.success_connects;
		});
}

function copyToClipboard(text, element) {
	// Create temporary input
	const tempInput = document.createElement("input");
	tempInput.value = text;
	document.body.appendChild(tempInput);
	tempInput.select();
	tempInput.setSelectionRange(0, 99999); // For mobile devices
	document.execCommand("copy");
	document.body.removeChild(tempInput);
	element.innerHTML = "COPIED";
	show_toast_message("Phone number copied successfully!", true);
}
function update_active_status(admin_id, status_type) {
	show_spinner();
	fetch("/admin-panel/api/update-active-status", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({
			admin_id: admin_id,
			status_type: status_type,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (data.error == false) {
				document.getElementById("be-active-btn").classList.toggle("d-none");
				document.getElementById("be-inactive-btn").classList.toggle("d-none");
				show_toast_message(data.message, true);
			} else {
				show_toast_message(data.message, false);
			}
		});
}
