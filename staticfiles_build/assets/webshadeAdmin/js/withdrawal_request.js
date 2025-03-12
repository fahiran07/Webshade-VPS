function update_withdrawal_status(withdrawal_id, status) {
	show_spinner();

	fetch("/admin-panel-124432/api/update-withdrawal-status/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ with_id: withdrawal_id, status: status }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (data.error === false) {
				document.getElementById("status-" + withdrawal_id).innerText = status;
				show_toast_message(data.message, true);
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function search(search_term, data_type) {
	show_spinner();

	if (previews_html === "") {
		previews_html = data_table.innerHTML;
	}

	fetch("/admin-panel-124432/api/search/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ search_term: search_term, data_type: data_type }),
	})
		.then((response) => response.json())
		.then((data) => {
			hide_spinner();
			if (data.search_result === false) {
				show_toast_message("Result not found", false);
			} else {
				data_table.innerHTML = "";
				data.search_result.forEach((item) => {
					let search_html = `
                    <tr>
                        <td>${item.with_id}</td>
                        <td>${item.phone}</td>
                        <td>${item.amount}</td>
                        <td>${item.account}</td>
                        <td>${item.ifsc}</td>
                        <td>${item.date}</td>
                        <td id="status-${item.with_id}">${item.status}</td>
                        <td>
                            <button class="bg-success px-2 fs-8 rounded-1 py-1 text-light border-0 me-2"
                                onclick="update_withdrawal_status('${item.with_id}', 'Success')">
                                Accept
                            </button>
                            <button class="bg-danger px-2 fs-8 rounded-1 py-1 text-light border-0"
                                onclick="update_withdrawal_status('${item.with_id}', 'Failed')">
                                Reject
                            </button>
                        </td>
                    </tr>
                `;
					data_table.innerHTML += search_html;
				});
			}
		});
}

function reset_search(input_value) {
	if (input_value === "" && previews_html !== "") {
		data_table.innerHTML = previews_html;
	}
}
