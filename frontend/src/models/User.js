export class User {
    constructor(id, name, email, role) {
      this.id = id;
      this.name = name;
      this.email = email;
      this.role = role;
    }  
    getName() {
      return this.name;
    }
    getEmail() {
        return this.email;
    }
  }
  