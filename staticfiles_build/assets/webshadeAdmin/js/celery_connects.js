function get_celery_data() {
	fetch("/admin-panel-124432/api/get-celery-data/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
	})
		.then((response) => response.json())
		.then((data) => {
			let total_task = document.getElementById("total-task");
			let active_task = document.getElementById("active-task");
			let schedule_task = document.getElementById("reserved-task");
			let reserved_task = document.getElementById("reserved-task");
			total_task = data.total_task;
			active_task = data.active_task;
			reserved_task = data.reserved_task;
			schedule_task = data.schedule_task;

			let dataTable = document.getElementById("data-table");
			dataTable.innerHTML = ""; // Clear existing table data

			data.tasks.forEach((task) => {
				let row = `
                    <tr>
                        <td>${task.id}</td> <!-- Task ID -->
                        <td>${task.name}</td> <!-- Task Name -->
                        <td>
                            <span class="${task.status === "Active" ? "text-success" : task.status === "Scheduled" ? "text-warning" : "text-secondary"}">
                                ${task.status}
                            </span>
                        </td> <!-- Status -->
                        <td>${task.timestamp || "N/A"}</td> <!-- Start Time -->
                    </tr>
                `;
				dataTable.innerHTML += row;
			});
		});
}
setInterval(() => {
	get_celery_data();
}, 1500);
