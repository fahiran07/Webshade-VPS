function loadAdminData() {
	fetch("/admin-panel/api/get-admin-data/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({}),
	})
		.then((response) => response.json())
		.then((data) => {
			if (data.error === false) {
				let request_admins = data.request_admins;
				document.getElementById("total-admin").innerText = data.total_admins;
				document.getElementById("revenue").innerText = data.revenue;
				document.getElementById("success-connects").innerText = data.success_connects;
				document.getElementById("failed-connects").innerText = data.failed_connects;
				request_admins.forEach((admin) => {
					// Update numeric/text values
					document.getElementById(`admin-revenue-${admin.admin_id}`).innerText = admin.total_revenue;
					document.getElementById(`admin-profit-${admin.admin_id}`).innerText = admin.profit;
					document.getElementById(`admin-payment-${admin.admin_id}`).innerText = admin.payment;
					document.getElementById(`admin-success-${admin.admin_id}`).innerText = admin.success_task;
					document.getElementById(`admin-failed-${admin.admin_id}`).innerText = admin.failed_task;
					document.getElementById(`admin-active-${admin.admin_id}`).innerText = admin.active_task;
					// Update status icon
					let statusTd = document.getElementById(`admin-status-${admin.admin_id}`);
					if (admin.active) {
						statusTd.innerHTML = `<i class="fas fa-check-circle" style="color: green"></i>`;
					} else {
						statusTd.innerHTML = `<i class="fas fa-times-circle" style="color: red"></i>`;
					}
				});
				setTimeout(() => {
					loadAdminData();
				}, 1000);
			} else {
				show_toast_message(data.message, false);
			}
		});
}

setTimeout(() => {
	loadAdminData();
}, 1500);
