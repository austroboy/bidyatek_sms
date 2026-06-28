//DOM purota load hle tarpor execute koro.
document.addEventListener("DOMContentLoaded", () => {
  const classRoutineForm = document.querySelector("#classRoutineForm");
  const subjects = document.querySelectorAll(".subject");
  const periods = document.querySelectorAll(".period");
  const scheduleContainer = document.getElementById("schedule");
  const tableCollapseButton = document.getElementById("table-collapse-button");
  const deleteButtons = document.querySelectorAll(".delete");
  classRoutineForm.addEventListener("submit", saveRoutine);

  deleteButtons.forEach((item) => {
    item.addEventListener("click", deleteContent);
  })

  function copyPasteFeature(columnCount, index, singleDayPeriods) {
    const copyIcons = document.querySelectorAll(".day-label i.bx-copy");
    const copyIcon = copyIcons[index];
    copyIcon.addEventListener("click", () => {
      const pasteIcons = document.querySelectorAll(".day-label i.bx-paste");
      pasteIcons.forEach((pasteIcon, index) =>
        pasteIcon.addEventListener("click", () => {
          const allPeriods = document.querySelectorAll(`div.period`);
          for (let i = 0; i < columnCount; i++) {
            allPeriods[columnCount * index + i].innerHTML =
              singleDayPeriods[i].innerHTML;
            // break will not have a delete button. so optional chaining.
            allPeriods[columnCount * index + i]
              .querySelector(".delete")
              ?.addEventListener("click", deleteContent);
          }
        })
      );
    });
  }

  const daysCount = document
    .querySelector("#schedule")
    .getAttribute("data-wdays");

  for (i = 0; i < Number(daysCount); i++) {
    const periods = Array.from(document.querySelectorAll(".period"));
    const columnCount = document
      .querySelector("#schedule")
      .getAttribute("data-periods");

    const start = i * columnCount;
    const end = start + columnCount;

    // Get columnCount divs for this iteration
    const selectedDivs = periods.slice(start, end);

    copyPasteFeature(columnCount, i, selectedDivs);
  }

  subjects.forEach((subject) => {
    subject.addEventListener("dragstart", dragStart);
  });

  //add eventListern to the existing dummy period fields. So, that the initail routine can also be editable.
  periods.forEach((period) => {
    period.addEventListener("dragover", dragOver);
    period.addEventListener("dragleave", dragLeave);
    period.addEventListener("drop", drop);
  });

  //uses the dataTransfer property of the event object (e.dataTransfer). This object allows to set and retrieve data associated with the drag operation.

  function dragStart(e) {
    e.dataTransfer.setData("text/plain", e.target.innerHTML);
  }

  //dragOver and dragLeave combinely, gives a hover like effect. That when the content is put over, the border becomes blue.

  // the dragover event triggered when a draggable element (subject) is dragged over a potential drop target (period).

  // It uses e.currentTarget.classList.add("drag-over"). e.currentTarget refers to the element that the event listener is attached to.
  function dragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add("drag-over");
  }

  //remove the classsList if the dragable element is removed.
  function dragLeave(e) {
    e.currentTarget.classList.remove("drag-over");
  }

  //represents the drop event triggered when a draggable element (subject) is dropped on a target element (period).
  function drop(e) {
    //prevent the browser's default behavior for the drop event.
    e.preventDefault();
    //remove the drag-over class if the element is dropped.
    e.currentTarget.classList.remove("drag-over");
    //retrieves the transferred data
    const text = e.dataTransfer.getData("text/plain");

    // remove subject if ther is already a subject
    const prevSubject = e.currentTarget.querySelector(".subject");
    if (prevSubject) {
      prevSubject.remove();
    }

    //create e new div and place the div on the period block.
    const clonedSubject = document.createElement("div");
    clonedSubject.className = "subject";
    clonedSubject.innerHTML = text;
    
    // const deleteButton = document.createElement("button");
    // deleteButton.setAttribute("type", "button");
    // deleteButton.className = "delete";
    // deleteButton.innerText = "X";
    // deleteButton.addEventListener("click", deleteContent);
    e.currentTarget.appendChild(clonedSubject);
    // e.currentTarget.appendChild(deleteButton);
  }

  function deleteContent(e) {
    console.log('deleteContent')
    //preventing event bubbling
    e.stopPropagation();
    //retrieves the parent element of the clicked delete button using e.currentTarget.parentElement.
    const periodDiv = e.currentTarget.parentElement;
    const subjectElement = periodDiv.querySelector(".subject");
    subjectElement.remove();
    // periodDiv.innerHTML = '<button type="button" class="delete">X</button>';
    periodDiv.querySelector(".delete").addEventListener("click", deleteContent);
  }

  function saveRoutine(e) {
    //create an empty object
    const routineData = [];

    // Get the data-working-days attribute
    const workingDaysData = document
      .getElementById("schedule")
      .getAttribute("data-working-days");

    // Parse the JSON data into an array
    const workingDays = JSON.parse(workingDaysData);

    console.log(workingDays)

    workingDays.forEach((day) => {
      //uses querySelectorAll to select all period elements with class period whose IDs start with the lowercase three-letter abbreviation of the current day followed by "-p"
      const dayPeriods = scheduleContainer.querySelectorAll(
        `.period[id^="${day.toLowerCase()}-p"]`
      );

      console.log(dayPeriods)

      //It iterates through the selected dayPeriods using another forEach loop.
      dayPeriods.forEach((period) => {
        const period_id = period.querySelector("input[name='period_id']")
          ? period.querySelector("input[name='period_id']").value
          : null;
        const class_id = period.querySelector("input[name='class_id']")
          ? period.querySelector("input[name='class_id']").value
          : null;
        const subject_id = period.querySelector("input[name='subject_id']")
          ? period.querySelector("input[name='subject_id']").value
          : null;
        const teacher_name = period.querySelector("input[name='teacher_name']")
          ? period.querySelector("input[name='teacher_name']").value
          : null;

        if (subject_id) {
          const periodElement = {
            period_id,
            class_id,
            subject_id,
            teacher_name,
            day_name: day,
          };
          routineData.push(periodElement);
        }
      });
    });
    
    document.querySelector('#routine_data').value = JSON.stringify(routineData);
  }

  tableCollapseButton.addEventListener("click", () => {
    // scheduleContainer.classList.toggle("collapsed");
    if (scheduleContainer.classList.contains("collapsed")) {
      scheduleContainer.classList.remove("collapsed");
      tableCollapseButton.innerText = "Collapse Routine";
    } else {
      scheduleContainer.classList.add("collapsed");
      tableCollapseButton.innerText = "Expand Routine";
    }
  });
});
