let add_revenue = document.getElementById("add-revenue");

function show_hide_revenue_form() {
	add_revenue.classList.toggle("d-none");
}

function submit_revenue_record() {
	let admin_id = document.getElementById("admin-id").value.trim();
	let amount = document.getElementById("withdraw-amount").value.trim();
	let balance = document.getElementById("last-balance").value.trim();

	fetch("/admin-panel/api/submit-revenue-record/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({
			admin_id: admin_id,
			amount: amount,
			balance: balance,
		}),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error == false) {
				show_hide_revenue_form();
				show_toast_message("Revenue Record Submitted Successfully", true);

				// ✅ Get the returned data
				const record = data.data;

				// ✅ Create a new row
				let newRow = `
				<tr>
					<td>${record.revenue_id}</td>
					<td>${record.admin_id}</td>
					<td>${record.admin_name}</td>
					<td>${record.last_balance}</td>
					<td>${record.withdraw_amount}</td>
					<td>${record.date}</td>
					<td><a href="admin/webshadeAdmin/revenuerecord/${revenue.id}/change/" target="_blank">EDIT</a></td>
				</tr>
			`;

				// ✅ Append to table
				document.getElementById("data-table").insertAdjacentHTML("afterbegin", newRow);

				// ✅ Clear input fields (optional)
				document.getElementById("admin-id").value = "";
				document.getElementById("withdraw-amount").value = "";
				document.getElementById("last-balance").value = "";
			} else {
				show_toast_message(data.message, false);
			}
		});
}

function FetchRevenueData() {
	fetch("/admin-panel/api/revenue-data/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({}), // Empty body agar kuch send nahi karna
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error == false) {
				document.getElementById("total-revenue").innerText = data.total_revenue;
				document.getElementById("today-revenue").innerText = data.today_revenue;
				document.getElementById("yesterday-revenue").innerText = data.yesterday_revenue;
				document.getElementById("profit").innerText = data.profit;
			} else {
				show_toast_message(data.message, false);
			}
		});
}

setInterval(() => {
	FetchRevenueData();
}, 1000);
