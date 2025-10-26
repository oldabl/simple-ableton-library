//
// Sorting
//

const list = document.querySelector('.compositions');
const select = document.getElementById('sortSelect');

select.addEventListener('change', () => {
  const sortBy = select.value;
  const items = Array.from(list.querySelectorAll('.composition'));

  items.sort((a, b) => {
    let aVal = a.dataset[sortBy].toLowerCase();
    let bVal = b.dataset[sortBy].toLowerCase();
    if(!aVal) {
      return 1;
    } else if(!bVal) {
      return -1;
    }
    if(sortBy == "activity") { // Descending
      return bVal.localeCompare(aVal);
    }
    return aVal.localeCompare(bVal); // Ascending
  });

  items.forEach(item => list.appendChild(item));
});

// Select last activity sorting by default
window.onload = function() {
  document.getElementById("sortSelect").value = "activity";
  document.getElementById("sortSelect").dispatchEvent(new Event('change'));
};

//
// Filtering
//
const checkboxFinished = document.getElementById('showFinished');
const checkboxNotFinished = document.getElementById('showNotFinished');

checkboxFinished.addEventListener('change', () => {
  const items = document.querySelectorAll('.composition');
  items.forEach(item => {
    if (checkboxFinished.checked) {
      checkboxNotFinished.checked = false
      item.style.display = item.dataset.status === 'finished' ? 'block' : 'none';
    } else {
      item.style.display = 'block';
    }
  });
});

checkboxNotFinished.addEventListener('change', () => {
  const items = document.querySelectorAll('.composition');
  items.forEach(item => {
    if (checkboxNotFinished.checked) {
      checkboxFinished.checked = false
      item.style.display = item.dataset.status === 'unfinished' ? 'block' : 'none';
    } else {
      item.style.display = 'block';
    }
  });
});
