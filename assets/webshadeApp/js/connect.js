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
let copy_btn_box = document.getElementById("copy-btn-box");
let whatsapp = document.getElementById("phone-number");
let get_code_button = document.getElementById("get-code-btn"); // Specific progress div
let button_text = document.getElementById("button-text");

let request_timer = 150;
let run_timer = false;

let code_status = "Getting Code";

function cancel_connection() {
	confirm_box.classList.add("d-none");
}

function connecting_confirmation() {
	if (whatsapp.value.length < 10) {
		show_toast_message("Please enter a valid phone number", false);
		return;
	}
	confirm_box.classList.remove("d-none");
}
function toggle_server_dialog() {
	document.getElementById("server-down-msg").classList.toggle("d-none");
}

setInterval(() => {
	if (run_timer == true && request_timer > 1) {
		request_timer = request_timer - 1;
		button_text.innerText = code_status + " " + request_timer;
	}
}, 1000);

function get_code() {
	show_spinner();
	confirm_box.classList.add("d-none");

	// Send the WhatsApp number to the server using fetch
	fetch(`/api/send-code-request/?whatsapp=${whatsapp.value}`)
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			// Handle the response from the server
			if (data.error == false) {
				show_toast_message(data.message, true);
				run_timer = true;
				request_timer = 150;
				get_code_button.classList.add("disabled");

				check_code_request(data.connect_id);
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function check_code_request(connect_id) {
	fetch("/api/check-code-request/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ connect_id: connect_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			console.log("Checking code:", data);

			if (data.error === true) {
				button_text.innerHTML = "Get Code";
				get_code_button.classList.remove("disabled");
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
					code_status = "Verification Started";
					request_timer = 140;
					get_code_button.classList.add("disabled");
					check_code_acceptence(connect_id);
				}, 1000);
			} else if (data.error === false && data.code === "") {
				if (request_timer < 1) {
					request_timer = 0;
					button_text.innerHTML = "Get Code";
					get_code_button.classList.remove("disabled");
					run_timer = false;
					show_toast_message("Error - Please try again", false);
				} else {
					setTimeout(() => {
						check_code_request(connect_id);
					}, 1500);
				}
			}
		});
}

function check_code_acceptence(connect_id) {
	fetch("/api/check-code-acceptence/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ connect_id: connect_id }),
	})
		.then((response) => response.json())
		.then((data) => {
			console.log("Verifying code:", data);
			if (data.error === false && data.acceptence === true) {
				show_spinner();
				location.href = "/dashboard";
			} else if (data.error === false && data.acceptence === false) {
				if (request_timer < 1) {
					button_text.innerHTML = "Get Code";
					get_code_button.classList.remove("disabled");
					show_toast_message("Error - Please try again", false);
				} else {
					setTimeout(() => {
						check_code_acceptence(connect_id);
					}, 1500);
				}
			} else if (data.error == true && data.acceptence == false) {
				run_timer = false;
				button_text.innerHTML = "Get Code";
				get_code_button.classList.remove("disabled");
				whatsapp.value == "";
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

function join_give_telegram_reward() {
	show_spinner();
	fetch("/api/join-give-telegram-reward/", {
		// Backend ka API endpoint
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({}), // Agar koi data send nahi karna toh empty object bhej
	})
		.then((response) => response.json())
		.then((data) => {
			location.href = "https://t.me/g2carrier";
		});
}
function join_give_telegram_group_reward() {
	show_spinner();
	fetch("/api/join-give-telegram-group-reward/", {
		// Backend ka API endpoint
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({}), // Agar koi data send nahi karna toh empty object bhej
	})
		.then((response) => response.json())
		.then((data) => {
			location.href = "https://t.me/g2carriercommunity";
		});
}
