frappe.ready(() => {
    const urlParams = new URLSearchParams(window.location.search);
    window.oppName = urlParams.get('name'); // Store globally for sendNote()

    if (window.oppName) {
        refreshData();
    } else {
        frappe.msgprint("No Project ID found in URL.");
    }
});

function refreshData() {
    frappe.call({
        method: 'frappe.client.get',
        args: {
            doctype: 'Opportunity',
            name: window.oppName
        },
        callback: (r) => {
            console.log(r)
            const doc = r.message;
            renderChat(doc.notes || []);
            // Map Opportunity details to UI
            document.getElementById('opp-title').innerText = doc.opportunity_from === 'Lead' ? doc.lead_name : doc.customer_name;
            document.getElementById('opp-id').innerText = `Opportunity Number: ${doc.name}`;
            document.getElementById('opp-status').innerText = `State: ${doc.status}`;
            document.getElementById('opp-res').innerText = `Resolution: ${doc.custom_resolution || 'N/A'}`;
            document.getElementById('opp-date').innerText = `Date: ${doc.transaction_date}`;
            document.getElementById('opp-material').innerText = `doc.custom_material` || 'N/A';

        }
    });
}

function renderChat(notes) {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = notes.map(n => {
        const isMe = n.added_by === frappe.session.user;
        return `
            <div class="d-flex ${isMe ? 'justify-content-end' : 'justify-content-start'} mb-3">
                <div class="p-3 rounded ${isMe ? 'bg-primary text-white' : 'bg-white border'}" style="max-width: 75%;">
                    <small class="d-block mb-1" style="opacity: 0.8; font-size: 0.75rem;">
                        ${n.added_by.split('@')[0]} • ${frappe.datetime.global_date_format(n.creation)}
                    </small>
                    <div style="white-space: pre-wrap;">${n.note}</div>
                </div>
            </div>`;
    }).join('');
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
}

function sendNote() {
    const noteText = document.getElementById('new-note').value;
    if (!noteText.trim()) return;

    document.getElementById('btn-send').disabled = true;

    frappe.call({
        // Update the path to point to your app's API function
        method: 'scan_business_crm.logic.lead.add_opportunity_note', 
        args: {
            opportunity: window.oppName,
            note: noteText
        },
        callback: (r) => {
            if (r.message === "Success") {
                document.getElementById('new-note').value = '';
                refreshData(); // Refresh chat UI
            }
            document.getElementById('btn-send').disabled = false;
        },
        error: (r) => {
            document.getElementById('btn-send').disabled = false;
        }
    });
}