axios.get('http://127.0.0.1:8000/api/v1/movies/')
  .then(response => {
      // 박스오피스 순위
      const boxofficeMovies = response.data.boxoffice_movies;
      const boxofficeList = document.getElementById('boxoffice-movies-list');
      boxofficeMovies.forEach(movie => {
          const li = document.createElement('li');
          li.textContent = `Title: ${movie.title}, Rank: ${movie.rank}`;
          boxofficeList.appendChild(li);
      });

      // 평점 순
      const gradedMovies = response.data.graded_movies;
      const gradedList = document.getElementById('graded-movies-list');
      gradedMovies.forEach(movie => {
          const li = document.createElement('li');
          li.textContent = `Title: ${movie.title}, Average Grade: ${movie.average_grade || 0}`;
          gradedList.appendChild(li);
      });

      // 좋아요 순
      const likedMovies = response.data.liked_movies;
      const likedList = document.getElementById('liked-movies-list');
      likedMovies.forEach(movie => {
          const li = document.createElement('li');
          li.textContent = `Title: ${movie.title}, Likes: ${movie.like}`;
          likedList.appendChild(li);
      });
  })
  .catch(error => {
      console.error('Error fetching movies:', error);
  });
