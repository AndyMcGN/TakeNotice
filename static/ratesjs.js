// functions for the add page
change_number = 0;

function addRow()
{
    change_number++;
    var minBtns = document.querySelectorAll(".add-btn");
    minBtns.forEach(function(btn) {
        btn.style.display = "none";
    })

    var row = document.createElement("tr");
    row.setAttribute("id",`change_${change_number}`)
    row.innerHTML = `<td>Next Change</td><td><input type='date' name='date_${change_number}'></td><td><input type='text' placeholder='New Rate' name='rate_${change_number}'></td><td><button class="add-btn btn plus-minus-btn" type="button"onclick="addRow()"><i class="add-btn fas fa-plus-circle"></i></button>
                    <button class="add-btn btn plus-minus-btn" type="button"onclick="removeRow()"><i class="fas fa-minus-circle"></i></button></td>`;
    var rows = document.getElementById("table_rows");
    rows.appendChild(row);

}

function removeRow()
{
    var row = document.getElementById(`change_${change_number}`)
    console.log(row)
    row.remove();
    change_number--;

    if (change_number === 0) {
        firstAddRow = document.querySelector("#firstAddRow");
        firstAddRow.innerHTML = '<input type="number" step="0.01" placeholder="rate" name="start_rate"><button class="add-btn btn plus-minus-btn" type="button"onclick="addRow()"><i class="fas fa-plus-circle"></i></button>';
        console.log("first row");
        }
    else
        {
        var lastRow = document.getElementById(`change_${change_number}`)
        lastRow.innerHTML = `<td>Next Change</td><td><input type='date' name='date_${change_number}'></td><td><input type='text' placeholder='New Rate' name='rate_${change_number}'></td><td><button class="btn plus-minus-btn" type="button"onclick="addRow()"><i class="fas fa-plus-circle"></i></button>
                        <button class="add-btn btn plus-minus-btn" type="button"onclick="removeRow()"><i class="add-btn fas fa-minus-circle"></i></button></td>`;
        }

}

//functions for the index page

function showNotWithdrawn()
{
    var withdrawal = document.getElementById("withdrawal")
    withdrawal.style.display = "none";
    document.getElementById("notWithdrawn").style.display = "contents";
    clicked = document.getElementById("showNotWithdrawalBtn");
    clicked.className += " active";
    notClicked = document.getElementById("showWithdrawalBtn");
    notClicked.classList.remove("active");

}

function showWithdrawal()
{
    document.getElementById("notWithdrawn").style.display = "none";
    document.getElementById("noticeDate").style.display = "none";
    withdrawal.style.display = "contents";
    clicked = document.getElementById("showWithdrawalBtn");
    clicked.className += " active";
    notClicked = document.getElementById("showNotWithdrawalBtn");
    notClicked.classList.remove("active");


}

function showNoticeDate()
{
    document.getElementById("noticeDate").style.display = "revert";
    clicked = document.getElementById("showNoticeBtn");
    clicked.className += " active";
    notClicked = document.getElementById("showNoNoticeBtn");
    notClicked.classList.remove("active");
}

function noNoticeDate()
{
    document.getElementById("noticeDate").style.display = "none";
    clicked = document.getElementById("showNoNoticeBtn");
    clicked.className += " active";
    notClicked = document.getElementById("showNoticeBtn");
    notClicked.classList.remove("active");
}




/*
function toggleBreakdown()
{
    if(document.getElementById("breakdown").style.display == "none")
    {
        document.getElementById("breakdown").style.display = "block";
    }
    else
    {
        document.getElementById("breakdown").style.display = "none";
    }
} */

