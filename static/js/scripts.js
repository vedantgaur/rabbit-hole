document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('search-form');
    const gifContainer = document.getElementById('gif-container');
    const scrollArrow = document.getElementById('scroll-arrow');
    const content = document.getElementById('content');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const query = form.querySelector('input[name="query"]').value;

        // Show the rabbit GIF briefly
        gifContainer.style.display = 'block';
        setTimeout(() => {
            gifContainer.style.display = 'none';
        }, 700);

        try {
            const response = await fetch('/process_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const data = await response.json();
            console.log('Received data:', data);

            // Handle data (e.g., display content, animation, music)
            content.innerHTML = `<h2>${query}</h2>${data.content}`;
            content.style.display = 'block';

            // Add subtopics
            const subtopicsList = document.createElement('ul');
            data.subtopics.forEach(subtopic => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="#" class="subtopic">${subtopic}</a>`;
                subtopicsList.appendChild(li);
            });
            content.appendChild(subtopicsList);

            // Show and animate the arrow after query processing
            scrollArrow.style.display = 'block';
            scrollArrow.style.animation = 'bounce 2s infinite';

            // Add event listeners for key terms and subtopics
            addContentEventListeners();

        } catch (error) {
            console.error('Error fetching the query:', error);
            // Display error message to the user
            content.innerText = `An error occurred: ${error.message}`;
            content.style.display = 'block';
        }
    });

    // Smooth scroll to content when arrow is clicked
    scrollArrow.addEventListener('click', () => {
        content.scrollIntoView({ behavior: 'smooth' });
    });

    function addContentEventListeners() {
        // Add event listeners for key terms
        document.querySelectorAll('.key-term').forEach(term => {
            term.addEventListener('click', async (e) => {
                e.preventDefault();
                const subtopic = e.target.textContent;
                await generateSubtopicContent(subtopic, e.target);
            });
        });

        // Add event listeners for subtopics
        document.querySelectorAll('.subtopic').forEach(subtopic => {
            subtopic.addEventListener('click', async (e) => {
                e.preventDefault();
                const subtopicText = e.target.textContent;
                await generateSubtopicContent(subtopicText, e.target);
            });
        });
    }

    async function generateSubtopicContent(subtopic, clickedElement) {
        try {
            const response = await fetch('/get_subtopic', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ subtopic: subtopic })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Create a new div for the subtopic content
            const subtopicDiv = document.createElement('div');
            subtopicDiv.className = 'subtopic-content';
            subtopicDiv.innerHTML = `<h3>${subtopic}</h3>${data.main_content}`;

            // Create a line connecting the clicked element to the new content
            const line = createConnectingLine(clickedElement, subtopicDiv);

            // Append the line and new content to the main content div
            content.appendChild(line);
            content.appendChild(subtopicDiv);

            // Scroll to the new content
            subtopicDiv.scrollIntoView({ behavior: 'smooth' });

            // Add event listeners to the new content
            addContentEventListeners();

        } catch (error) {
            console.error('Error fetching subtopic:', error);
        }
    }

    function createConnectingLine(startElement, endElement) {
        const line = document.createElement('div');
        line.className = 'connecting-line';

        const startRect = startElement.getBoundingClientRect();
        const endRect = endElement.getBoundingClientRect();

        const startX = startRect.right;
        const startY = startRect.top + startRect.height / 2;
        const endX = endRect.left;
        const endY = endRect.top;

        const length = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
        const angle = Math.atan2(endY - startY, endX - startX) * 180 / Math.PI;

        line.style.width = `${length}px`;
        line.style.transform = `rotate(${angle}deg)`;
        line.style.top = `${startY}px`;
        line.style.left = `${startX}px`;

        return line;
    }
});