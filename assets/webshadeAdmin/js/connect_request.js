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
		body: JSON.stringify({ connect_id: connectId, admin_id: "admin" }),
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
		body: JSON.stringify({ connect_id: connectId, admin_id: "admin" }),
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

function fetchConnectionRequestData() {
	fetch("/admin-panel/api/connects-request-data/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json", // JSON data bhejne ke liye
		},
		body: JSON.stringify({}), // Agar koi data send nahi karna toh empty object bhej
	})
		.then((response) => response.json())
		.then((data) => {
			document.getElementById("total-connects").innerText = data.total_connects;
			document.getElementById("processing-connects").innerText = data.processing_connects;
			document.getElementById("online-connects").innerText = data.online_connects;
			document.getElementById("offline-connects").innerText = data.offline_connects;
		})
		.catch((error) => console.error("Error fetching dashboard data:", error));
}

// Page load hone pe fetch call karne ke liye
document.addEventListener("DOMContentLoaded", fetchConnectionRequestData);

setInterval(() => {
	fetchConnectionRequestData();
}, 1000);
