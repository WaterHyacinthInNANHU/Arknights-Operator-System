package org.qxdn.akts.dao;

import org.qxdn.akts.model.User;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends CrudRepository<User, Integer> {

    User findUserByEmail(String email);

    User findUserById(Integer id);
}
