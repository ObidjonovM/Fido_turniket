function getOptionValue1(sel) {
    let hidden_username = document.getElementById('hidden_username');
    let hidden_dept_id = document.getElementById('hidden_dept_id');
    let hidden_job_id = document.getElementById('hidden_job_id');
    hidden_username.value = sel.options[sel.selectedIndex].text;
    hidden_dept_id.value = sel.options[sel.selectedIndex].getAttribute('dept_id');
    hidden_job_id.value = sel.options[sel.selectedIndex].getAttribute('job_id');
}
