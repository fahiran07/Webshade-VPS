let toast_message_box = document.getElementById("message-box");
let toast_message = document.getElementById("toast-message");
let search_spinner = document.getElementById("search-spinner");
let csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
let spinner = document.getElementById("spinner");

function toggle_menu() {
	let menu = document.getElementById("menu");
	menu.classList.toggle("active");
	document.getElementsByTagName("html")[0].classList.toggle("overflow-hidden");
	document.getElementsByTagName("body")[0].classList.toggle("overflow-hidden");
}

function show_toast_message(message, is_success) {
	if (is_success) {
		toast_message.innerHTML = `
            <div class="d-flex-center">
                <i class="fas fa-check-circle me-2 fs-4"></i>
            </div>
            <div>
                <p class="mb-0 fs-7" id="toast-type">Success</p>
                <p class="mb-0 fs-8" id="toast-message-text">${message}</p>
            </div>`;
		toast_message.classList.add("success-toast");
		toast_message.classList.remove("error-toast");
	} else {
		toast_message.innerHTML = `
            <div class="d-flex-center">
                <i class="fas fa-times-circle me-2 fs-4"></i>
            </div>
            <div>
                <p class="mb-0 fs-7" id="toast-type">Error</p>
                <p class="mb-0 fs-8" id="toast-message-text">${message}</p>
            </div>`;
		toast_message.classList.add("error-toast");
		toast_message.classList.remove("success-toast");
	}

	toast_message_box.classList.remove("d-none");

	setTimeout(() => {
		toast_message.classList.add("show-toast");
		setTimeout(() => {
			toast_message.classList.remove("show-toast");
			setTimeout(() => {
				toast_message_box.classList.add("d-none");
			}, 200);
		}, 1000);
	}, 50);
}

function show_spinner() {
	spinner.classList.remove("d-none");
}

function hide_spinner() {
	spinner.classList.add("d-none");
}

function show_search_spinner() {
	search_spinner.classList.remove("d-none");
}

function hide_search_spinner() {
	search_spinner.classList.add("d-none");
}

function scroll_to_bottom() {
	window.scrollTo({
		top: document.documentElement.scrollHeight,
		behavior: "smooth",
	});
}
