let data_table = document.getElementById("data-table"),
	previews_table,
	current_search_term,
	newStatus;

function toggleActiveStatus(user_id, status) {
	console.log(status);
	newStatus = status == "135";

	fetch("/admin-panel/api/update_user_status/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ user_id: user_id, active: newStatus }),
	})
		.then((response) => response.json())
		.then((data) => {
			var statusElement;
			if (data.error == 0) {
				statusElement = document.getElementById("user-status-" + user_id);
				if (statusElement) {
					if (newStatus == 1) {
						statusElement.innerHTML = '<i class="fas fa-check" style="color: green"></i>';
					} else {
						statusElement.innerHTML = '<i class="fas fa-times" style="color: red"></i>';
					}
				}
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function search(query) {
	show_spinner();
	current_search_term = query.trim();

	fetch("/admin-panel/api/get-user-data/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({ search_term: query }),
	})
		.then((response) => response.json())
		.then((data) => {
			console.log(data);
			hide_spinner();

			if (data.error == 0) {
				previews_table = data_table.innerHTML;
				let user = data.result;

				data_table.innerHTML = `
                <tr>
                    <td>
                        <p class="mb-0">${user.user_id}</p>
                    </td>
                    <td>
                        <p class="mb-0">${user.phone}</p>
                        <p class="mb-0">${user.email}</p>
                        <p class="mb-0">${user.password}</p>
                    </td>
                    <td>
                        <div class="hr-4 wr-4">
                            <p class="mb-0">${user.refer_by || "-"}</p>
                            ${user.active ? '<i class="fas fa-check" style="color: green"></i>' : '<i class="fas fa-times" style="color: red"></i>'}
                        </div>
                    </td>
                    <td>
                        <p>₹${user.balance}.00</p>
                    </td>
                    <td>
                        <p>₹${user.commision}.00</p>
                    </td>
                </tr>
            `;
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function reset_search(query) {
	if (query !== current_search_term && current_search_term !== null && previews_table !== null) {
		data_table.innerHTML = previews_table;
	}
}
