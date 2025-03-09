let withdraw_amount = 110;
let withdraw_btn = document.getElementById("withdraw-btn");
let bank_submit_btn = document.getElementById("submit-btn");
let loading_box = document.getElementById("loading-box");
let bank_info_box = document.getElementById("bank-info-box");
let status_msg = document.getElementById("withdraw-msg");
let status_msg_box = document.getElementById("status-msg-box");
let balance = document.getElementById("balance");
let withdraw_option = document.getElementsByClassName("withdraw-option");
let actual_withdraw_amount = 100;

function set_withdraw_amount(amount, element) {
	let withdraw_amount_display = document.getElementById("withdraw-amount"),
		bank_fee_display = document.getElementById("bank-fee");

	actual_withdraw_amount = amount;

	// Remove 'active' class from all options
	for (let i = 0; i < withdraw_option.length; i++) {
		withdraw_option[i].classList.remove("active-amount");
	}

	// Add 'active' class to selected option
	element.classList.add("active-amount");

	// Calculate total withdrawal amount with 10% fee
	withdraw_amount = amount + (amount / 100) * 10;
	withdraw_amount_display.innerText = withdraw_amount;
	bank_fee_display.innerText = (amount / 100) * 10;

	// Enable or disable withdraw button based on balance
	if (balance.innerHTML >= withdraw_amount) {
		withdraw_btn.classList.add("active-submit-btn");
	} else {
		withdraw_btn.classList.remove("active-submit-btn");
	}
}

function show_bank_info_box() {
	bank_info_box.classList.toggle("d-none");
}

// Enable withdraw button if balance is sufficient
if (balance.innerHTML >= 110) {
	withdraw_btn.classList.add("active-submit-btn");
}

// Handle bank account submission
bank_submit_btn.addEventListener("click", () => {
	document.getElementById("main-spinner").classList.remove("d-none");

	let holder_name = document.getElementById("holder-name"),
		account_number = document.getElementById("account-number"),
		ifsc_code = document.getElementById("ifsc-code");

	fetch("/api/add-bank-account/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({
			holder_name: holder_name.value,
			ifsc_code: ifsc_code.value,
			account_number: account_number.value,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			document.getElementById("main-spinner").classList.add("d-none");

			if (data.error) {
				show_toast_message(data.message, false);
			} else {
				show_toast_message(data.message, true);
				document.getElementById("bank-box").innerText = account_number.value + "(" + holder_name.value + ")";
				setTimeout(() => {
					show_bank_info_box();
				}, 1500);
			}
		});
});

// Handle withdraw request
withdraw_btn.addEventListener("click", () => {
	if (withdraw_btn.classList.contains("active-submit-btn")) {
		document.getElementById("main-spinner").classList.remove("d-none");

		fetch("/api/withdrawal/", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": csrfToken,
			},
			body: JSON.stringify({ amount: actual_withdraw_amount }),
		})
			.then((response) => response.json())
			.then((data) => {
				document.getElementById("main-spinner").classList.add("d-none");

				if (data.error) {
					show_toast_message(data.message, false);
				} else {
					balance.innerHTML = data.balance;
					show_toast_message(data.message, true);
					setTimeout(() => {
						show_spinner();
						location.href = "/account/";
					}, 1500);
				}
			});
	}
});
