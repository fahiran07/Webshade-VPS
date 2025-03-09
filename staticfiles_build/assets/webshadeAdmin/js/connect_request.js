let currentConnectId = null;

function showCodeBox(connectId) {
	currentConnectId = connectId;
	document.getElementById("code_box").classList.remove("d-none");
}

function hideCodeBox() {
	document.getElementById("code_box").classList.add("d-none");
}

function acceptRequest(connectId) {
	show_spinner();
	fetch("/admin-panel/api/accept-request/", {
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
				document.getElementById(`status-${connectId}`).innerText = "Online";
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function rejectRequest(connectId) {
	fetch("/admin-panel/api/reject-request/", {
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
				document.getElementById(`status-${connectId}`).innerText = "Rejected";
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function sendCode() {
	let code = document.getElementById("code").value;
	show_spinner();
	fetch("/admin-panel/api/send-code/", {
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

let previewsHtml = "",
	dataTable = document.getElementById("data-table");

function search(searchTerm, dataType) {
	show_spinner();
	if (previewsHtml === "") {
		previewsHtml = dataTable.innerHTML;
	}

	fetch("/admin-panel/api/search/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ search_term: searchTerm, data_type: dataType }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (!data.search_result) {
				reset_search(searchTerm);
				show_toast_message("Result not found", false);
			} else {
				dataTable.innerHTML = data.search_result
					.map(
						(connect) => `
                    <tr>
                        <td>${connect.connect_id}</td>
                        <td>${connect.user_id}</td>
                        <td>${connect.whatsapp}</td>
                        <td>${connect.date}</td>
                        <td>${connect.time}</td>
                        <td id="status-${connect.connect_id}">${connect.status}</td>
                        <td>
                            <button class="bg-success px-3 fs-9 rounded-1 py-1 text-light border-0 me-2" 
                                onclick="acceptRequest('${connect.connect_id}')">Accept</button>
                            <button class="bg-danger px-3 fs-9 rounded-1 py-1 text-light border-0" 
                                onclick="rejectRequest('${connect.connect_id}')">Reject</button>
                        </td>
                        <td>
                            <button class="bg-primary px-2 rounded-1 py-1 text-light border-0" 
                                onclick="showCodeBox('${connect.connect_id}')">Send Code</button>
                        </td>
                    </tr>
                `
					)
					.join("");
			}
		});
}

function reset_search(query) {
	if (query == "" && previewsHtml !== null) {
		dataTable.innerHTML = previewsHtml;
	}
}
