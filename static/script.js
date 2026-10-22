function renderTaskCard(task) {
      // Prevent duplicates if the card already exists on the board
      if (document.getElementById('task-' + task.id)) return;

      var card = document.createElement('div');
      card.className = 'task-card';
      card.id = 'task-' + task.id;
      card.draggable = true;
      card.textContent = task.title;
      card.ondragstart = (e) => e.dataTransfer.setData('text/plain', task.id);

      var targetList = document.getElementById(task.status + '-list');
      if (targetList) targetList.appendChild(card);
    }
