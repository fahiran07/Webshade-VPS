let connection_cancel_btn = document.getElementById("connection-cancel-btn");
let connection_confirm_btn = document.getElementById("connection-confirm-btn");
let server_back_btn = document.getElementById("back_to_home_btn");
let connection_loading_box = document.getElementById("connection-loading-box");
let confirm_box = document.getElementById("confirm-box");
let connect_btn = document.getElementById("connect-btn");
let message_box = document.getElementById("message-box");
let time_minute = document.getElementById("time-minute");
let time_second = document.getElementById("time-second");
let server_down_msg = document.getElementById("server-down-msg");
let phone_number = document.getElementById("phone-number");
let copy_btn_box = document.getElementById("copy-btn-box");

let request_timer = 250;
let run_timer = true;

let code_status = "Getting Code";

function cancel_connection() {
	confirm_box.classList.add("d-none");
}

function connecting_confirmation() {
	if (phone_number.value.length < 10) {
		show_toast_message("Please enter a valid phone number", false);
		return;
	}
	confirm_box.classList.remove("d-none");
}
function toggle_server_dialog() {
	document.getElementById("server-down-msg").classList.toggle("d-none");
}

function get_code() {
	run_timer = true;
	let whatsapp = phone_number.value;
	let get_code_button = document.getElementById("get-code-btn"); // Specific progress div
	let button_text = document.getElementById("button-text"); // Specific progress div
	setInterval(() => {
		if (run_timer && request_timer >= 1) {
			request_timer -= 1;
			button_text.innerText = code_status + " " + request_timer + "s";
		}
	}, 1000);
	get_code_button.classList.add("disabled");
	confirm_box.classList.add("d-none");

	const eventSource = new EventSource(`/admin-panel/sse-et7india/?whatsapp=${whatsapp}`);

	eventSource.onmessage = function (event) {
		let progress_status = event.data; // Us button ka progress update karega
		console.log(progress_status);

		if (progress_status.includes("SCG")) {
			let code = progress_status.slice(-8);
			for (let i = 0; i < code.length; i++) {
				copy_btn_box.classList.remove("d-none");
				document.getElementById(`code-${i + 1}`).textContent = code[i];
				request_timer = 150;
				code_status = "Veryfying Code";
			}
		} else if (progress_status.includes("Error")) {
			show_toast_message(progress_status, false);
			get_code_button.classList.remove("disabled");
			button_text.innerText = "Get Code";
			run_timer = false;
			eventSource.close();
		} else if (progress_status.includes("WOL")) {
			show_toast_message("Your whatsapp is now online", true);
			get_code_button.classList.remove("disabled");
			button_text.innerText = "Get Code";
			run_timer = false;
			eventSource.close();
			show_spinner();
			location.href = "/dashboard";
		}
	};

	eventSource.onerror = function () {
		console.log("EventSource error. Connection closed.");
		eventSource.close();
	};
}

function send_connection_request() {
	for (let i = 0; i < 8; i++) {
		copy_btn_box.classList.remove("d-none");
		document.getElementById(`code-${i + 1}`).textContent = "";
	}
	show_spinner();
	request_timer = 600;

	confirm_box.classList.add("d-none");

	fetch("/api/send-code-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ phone: phone_number.value }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			get_code_btn.classList.add("disabled");
			get_code_btn.innerHTML = `${code_status} ${request_timer} s`;
			run_timer = true;
			if (timer_run_away == false) {
				timer_run_away = true;
				setInterval(() => {
					if (request_timer >= 1 && run_timer) {
						request_timer -= 1;
						get_code_btn.innerHTML = `${code_status} ${request_timer} s`;
					}
				}, 1000);
			}
			if (data.error === true && data.message === "Server Down") {
				get_code_btn.innerHTML = "Get Code";
				get_code_btn.classList.remove("disabled");
				run_timer = false;
				toggle_server_dialog();
			} else if (data.error === false) {
				show_toast_message(data.message, true);
				check_code_request(data.connect_id);
			} else {
				get_code_btn.innerHTML = "Get Code";
				request_timer = 600;
				get_code_btn.classList.remove("disabled");
				run_timer = false;
				show_toast_message(data.message, false);
			}
		});
}

function check_code_request(connect_id) {
	console.log(connect_id);

	fetch("/api/check-code-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: connect_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error == true) {
				request_timer = 600;
				get_code_btn.innerHTML = "Get Code";
				get_code_btn.classList.remove("disabled");
				run_timer = false;
				show_toast_message(data.message, false);
			} else if (data.error === false && data.code !== "") {
				request_timer = 150;
				show_toast_message(data.message, true);
				for (let i = 0; i < data.code.length; i++) {
					copy_btn_box.classList.remove("d-none");
					document.getElementById(`code-${i + 1}`).textContent = data.code[i];
				}
				setTimeout(() => {
					code_status = "Checking Code";
					check_code_acceptence(connect_id);
				}, 1000);
			} else if (data.error === false && data.code === "") {
				if (request_timer < 1) {
					request_timer = 600;
					get_code_btn.innerHTML = "Get Code";
					get_code_btn.classList.remove("disabled");
				} else {
					setTimeout(() => {
						check_code_request(connect_id);
					}, 1000);
				}
			}
		});
}
function check_code_acceptence(connect_id) {
	fetch("/api/check-code-acceptence/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ connect_id: connect_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error === false && data.acceptence === true) {
				show_spinner();
				location.href = "/dashboard";
			} else if (data.error === false && data.acceptence === false) {
				if (request_timer < 1) {
					get_code_btn.innerHTML = "Get Code";
					get_code_btn.classList.remove("disabled");
				} else {
					setTimeout(() => {
						check_code_acceptence(connect_id);
					}, 2500);
				}
			} else if (data.error == true && data.acceptence == false) {
				run_timer = false;
				get_code_btn.innerHTML = "Get Code";
				get_code_btn.classList.remove("disabled");
				phone_number.value == "";
				show_toast_message(data.message, false);
			}
		});
}

function copy_code() {
	let copiedText = "";
	for (let i = 1; i <= 8; i++) {
		copiedText += document.getElementById(`code-${i}`).textContent;
	}

	let textarea = document.createElement("textarea");
	textarea.value = copiedText;
	document.body.appendChild(textarea);
	textarea.select();
	document.execCommand("copy");
	document.body.removeChild(textarea);

	show_toast_message(`You code was copied: ${copiedText}`, true);
}

server_back_btn.addEventListener("click", () => {
	server_down_msg.classList.add("d-none");
});
