let data_table = document.getElementById("data-table");
let previews_table;
let current_search_term;
let newStatus;

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
function fetchDashboardData() {
	fetch("/admin-panel/api/dashboard-data/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json", // JSON data bhejne ke liye
		},
		body: JSON.stringify({}), // Agar koi data send nahi karna toh empty object bhej
	})
		.then((response) => response.json())
		.then((data) => {
			document.getElementById("total-users").innerText = data.total_users;
			document.getElementById("today-users").innerText = data.today_users;
			document.getElementById("total-balance").innerText = data.total_balance;
			document.getElementById("total-commision").innerText = data.total_commision;
		})
		.catch((error) => console.error("Error fetching dashboard data:", error));
}

// Page load hone pe fetch call karne ke liye
document.addEventListener("DOMContentLoaded", fetchDashboardData);

setInterval(() => {
	fetchDashboardData();
}, 1000);
