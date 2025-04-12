async function startUp() {
    const form = document.getElementById('scrapeForm');
    const urlInput = document.getElementById('url');
    const loadingIcon = document.querySelector('.loading');
    const domainsList = document.getElementById('domainsList');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        loadingIcon.style.display = 'inline';
        try {
            const response = await fetch('/pages/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: urlInput.value })
            });
            if (response.ok) {
                const newPage = await response.json();
                addPageToList(newPage);
            } else {
                alert('Error: Unable to scrape the page.');
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            loadingIcon.style.display = 'none';
        }
    });

    async function fetchDomains() {
        try {
            const response = await fetch('/pages/');
            if (response.ok) {
                const data = await response.json();
                data.saved_domains.forEach(domain => {
                    
                    // "saved_domains": [
                    //     {
                    //     "domain": "fastapi.tiangolo.com",
                    //     "pages": [
                    //         {
                    //         "url": "/tutorial/query-params/",
                    //         "versions": [
                    //             {
                    //             "page_body": "67d842312b5fa11ba962f2be",
                    //             "save_time": "2025-03-17T15:39:32.962000",
                    //             "title": "Query Parameters - FastAPI",
                    //             "preview": "67d84127574d15c2781203d6"
                    //             }
                    //          }
                    //      ]
                    //     }
                    // ]
                    // }
                    
                    
                    // <div class="domainsList">
                    //     <div>
                    //         <h2>Domain base URL</h2>
                    //         <div class="pages-list">
                    //             <div class="page">
                    //                 <a href="page_full_url">original page</a>
                    //                 <div class="versions-list">
                    //                     <div class="page-component">
                    //                         <a href="">page version url</a>
                    //                         <img src="https://c49c45c3-2cf9-4ab2-ac46-fa1d8ebd66aa.mdnplay.dev/shared-assets/images/examples/grapefruit-slice.jpg">
                    //                     </div>
                    //                 </div>
                    //             </div>
                    //         </div>
                    //     </div>
                    // </div>
                    
                    const domainItem = document.createElement('div');
                    const domainTitle = document.createElement('h2');
                    domainTitle.textContent = domain.domain;
                    domainItem.appendChild(domainTitle);

                    const domainPagesList = document.createElement('div');
                    domainPagesList.className = "pages-list";
                    domain.pages.forEach(page => {
                        const pageItem = document.createElement('div');
                        pageItem.className = "page";

                        const pageLink = document.createElement('a');
                        pageLink.href = `https://${domain.domain}/${page.url}`;
                        pageLink.textContent = `Original URL: https://${domain.domain}/${page.url}`;
                        
                        const pageVersions = document.createElement('div');
                        pageVersions.className = "versions-list";
                        
                        page.versions.forEach(version => {
                            const versionItem = document.createElement('div');
                            const versionLink = document.createElement('a');
                            const versionPreview = document.createElement('img');
                            // const versionTimestamp = document.createElement('b');

                            // TODO: add time of scrapping
                            // TODO: add vertical scrolling (max height)??
                            
                            versionItem.className = "page-component";
                            versionLink.href = `/pages/${version.page_body}`;
                            versionLink.textContent = version.title;
                            versionPreview.src = `/statics/${version.preview}`;

                            versionItem.appendChild(versionLink);
                            versionItem.appendChild(versionPreview);

                            pageVersions.appendChild(versionItem);
                        });
                        // pageItem.style.paddingLeft = "20px";
                        pageItem.appendChild(pageLink);
                        pageItem.appendChild(pageVersions);
                        domainPagesList.appendChild(pageItem);
                    });
                    domainItem.appendChild(domainPagesList);

                    // domainTitle.addEventListener('click', () => {
                    //     domainPagesList.style.display = domainPagesList.style.display === 'none' ? 'block' : 'none';
                    // });

                    domainsList.appendChild(domainItem)
                });
            }
        }catch (error) {
            alert('Error: ' + error.message);
        } finally {
            loadingIcon.style.display = 'none';
        }
    }

    const reloadButton = document.createElement('button');
    reloadButton.textContent = 'Reload';
    reloadButton.addEventListener('click', async () => {
        domainsList.innerHTML = '';
        await fetchDomains();
    });
    form.parentNode.insertBefore(reloadButton, form.nextSibling);

    await fetchDomains();
};