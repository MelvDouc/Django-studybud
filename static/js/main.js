class Room extends HTMLElement {
  constructor() {
    super();

    this.innerHTML = `
    <h3>@${this.hostUsername}</h3>
    <a href="${this.pageUrl}">[${this.roomId}]</a>
    <span>${this.roomName}</span>
    <div>${this.topicName}</div>
    <div>
      <a href="${this.updateUrl}">Edit</a>
      <a href="${this.deleteUrl}">Delete</a>
    </div>
    `;
  }

  #getAttributeOrNull(attributeName) {
    return this.getAttribute(`data-${attributeName}`) || null;
  }

  get hostUsername() {
    return this.#getAttributeOrNull("host-username");
  }

  get pageUrl() {
    return this.#getAttributeOrNull("page-url");
  }

  get updateUrl() {
    return this.#getAttributeOrNull("update-url");
  }

  get deleteUrl() {
    return this.#getAttributeOrNull("delete-url");
  }

  get roomId() {
    return this.#getAttributeOrNull("room-id");
  }

  get roomName() {
    return this.#getAttributeOrNull("room-name");
  }

  get topicName() {
    return this.#getAttributeOrNull("topic-name");
  }
}

customElements.define("app-room", Room);