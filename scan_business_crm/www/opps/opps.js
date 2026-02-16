frappe.ready(() => {
    const statusMap = {
        "Open": { bg: "#fff3cd", color: "#856404" },
        "In Progress": { bg: "#cce5ff", color: "#004085" },
        "Completed": { bg: "#d4edda", color: "#155724" },
        "Cancelled": { bg: "#f8d7da", color: "#721c24" }
    };

    document.querySelectorAll('.badge-status').forEach(badge => {
        const status = badge.getAttribute('data-status');
        const style = statusMap[status];
        if (style) {
            badge.style.backgroundColor = style.bg;
            badge.style.color = style.color;
        } else {
            badge.style.backgroundColor = "#e2e3e5";
            badge.style.color = "#383d41";
        }
    });
});