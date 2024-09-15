document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('search-form');
    const gifContainer = document.getElementById('gif-container');
    const smallGifContainer = document.getElementById('small-gif-container');
    const scrollArrow = document.getElementById('scroll-arrow');
    const content = document.getElementById('content');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const query = form.querySelector('input[name="query"]').value;

        // Show the rabbit GIF
        gifContainer.innerHTML = `<img src="${gifContainer.querySelector('img').src}?t=${Date.now()}" alt="Rabbit Jumping">`;
        gifContainer.style.display = 'block';

        try {
            const response = await fetch('/process_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            // Hide the GIF after receiving the response
            gifContainer.style.display = 'none';

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const data = await response.json();
            console.log('Received data:', data);

            // Handle data (e.g., display content, animation, music)
            content.innerHTML = `<h2>${query}</h2>${data.content}`;
            content.style.display = 'block';

            // Trigger MathJax to render the LaTeX for the main content
            await MathJax.typeset();

            // Add subtopics with links for each generation
            const subtopicsList = document.createElement('ul');
            data.subtopics.forEach(subtopic => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="#" class="subtopic">${subtopic}</a>`;
                subtopicsList.appendChild(li);
            });
            content.appendChild(subtopicsList);

            // Show and animate the arrow after query processing
            scrollArrow.style.display = 'block'; // Keep the arrow visible
            scrollArrow.style.animation = 'bounce 2s infinite';

            // Add event listeners for key terms and subtopics
            addContentEventListeners();

        } catch (error) {
            console.error('Error fetching the query:', error);
            // Display error message to the user
            content.innerText = `An error occurred: ${error.message}`;
            content.style.display = 'block';
            // Hide the GIF in case of error
            gifContainer.style.display = 'none';
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

                // Show the small rabbit GIF
                smallGifContainer.style.display = 'block';
                smallGifContainer.innerHTML = `<img src="${smallGifContainer.querySelector('img').src}?t=${Date.now()}" alt="Rabbit Jumping">`;

                // Call a function to handle the subtopic content generation
                await generateSubtopicContent(subtopicText, e.target);
            });
        });
    }

    async function generateSubtopicContent(subtopic, clickedElement) {
        try {
            // Show the small rabbit GIF without animation
            smallGifContainer.style.display = 'block';
            smallGifContainer.innerHTML = `<img src="${smallGifContainer.querySelector('img').src}?t=${Date.now()}" alt="Rabbit Jumping">`;
            smallGifContainer.style.animation = 'none'; // Stop any animation

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

            // Append the new content
            content.appendChild(subtopicDiv);

            // Trigger MathJax to render the LaTeX
            await MathJax.typeset();

            // Scroll to the new content
            subtopicDiv.scrollIntoView({ behavior: 'smooth' });

            // Hide the small rabbit GIF when generation is complete
            smallGifContainer.style.display = 'none';

            // Add event listeners to the new content
            addContentEventListeners();
            
        } catch (error) {
            console.error('Error fetching subtopic:', error);
            // Hide the small rabbit GIF in case of error
            smallGifContainer.style.display = 'none';
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